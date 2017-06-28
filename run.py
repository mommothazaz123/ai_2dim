'''
Created on Jun 19, 2017

@author: andrew
'''

from datetime import datetime
import json
import math
import random
import threading

from lib.graphics import *
from lib.inputs import get_gamepad, UnpluggedError, get_key, devices


Y_MIN = 0
Y_MAX = 500
X_MIN = 0
X_MAX = 500

PROGRAM_SPEED = 1/20 # 20 tps

DIFFICULTY = int(input("Difficulty? (1, 2, or 3): ")) # (1, 2, 3)
while not DIFFICULTY in (1, 2, 3):
    DIFFICULTY = int(input("Difficulty? (1, 2, or 3): ")) # (1, 2, 3)

ON_TARGET = 10 # px to be considered on target, default 10
MAX_SPEED = 10 # px/tick

LEARN_RATE = 0.05
MAX_WEIGHT = 1 # 0.5 = slow, 1 = stable, 1-2 = oscillating, 2+ = unstable

if DIFFICULTY == 1:
    CONTROL_MAP = [1, 1] # randomize i/o
    CONTROL_FLIP = False
    CONTROL_RANDOMIZATION = False
elif DIFFICULTY == 2:
    CONTROL_MAP = [random.choice([-1, 1]), random.choice([-1, 1])] # randomize i/o
    CONTROL_FLIP = random.choice([True, False])
    CONTROL_RANDOMIZATION = False
else:
    CONTROL_MAP = [random.choice([-1, 1]), random.choice([-1, 1])] # randomize i/o
    CONTROL_FLIP = random.choice([True, False])
    CONTROL_RANDOMIZATION = True


class Program:
    def move_random(self, max_move_dist):
        a = round(max_move_dist/(20*3))
        a = min(3, a)
        a = 0
        self.robot.move(random.randint(-a, a), random.randint(-a, a))

p = Program()

class Robot(Circle):
    """A naive object with a few helper methods."""
    def __init__(self, x, y):
        center = Point(x, y)
        super().__init__(center, 7)
        self.setOutline('green')
        self.draw(p.win)
        self.reverse = False
        
    def getPos(self): # controller input
        return (self.getCenter().x, self.getCenter().y)
    
    def move(self, dx, dy): # controller output
        dx = dx * CONTROL_MAP[0]
        dy = dy * CONTROL_MAP[1]
        if CONTROL_FLIP:
            super().move(dy, dx)
        else:
            super().move(dx, dy)
        
class Controller:
    """This object should take input from the Robot and minimise delta."""
    def __init__(self, robot):
        self.robot = robot
        self.weights = [[0, 0], [0, 0]] # [[o1 on p1, o1 on p2], [o2 on p1, o2 on p2]]
        self.learned = [[0, 0], [0, 0]]
        self.learn_rate = LEARN_RATE
        self.last_output = None
    
    def get_delta(self, axis):
        """Returns a tuple."""
        return self.robot.getPos()[axis] - p.target[axis]
    
    def get_delta_total(self):
        return math.sqrt((self.robot.getPos()[0] - p.target[0])**2 + (self.robot.getPos()[1] - p.target[1])**2)
    
    def move_robot(self, control):
        hasWeight = True
        axis = None
        for a, w in enumerate(self.learned[control]):
            hasWeight = w > 20
            if not hasWeight:
                axis = a
                break
            
        if hasWeight:
            a = [self.weights[0][0] + self.weights[1][0], self.weights[0][1] + self.weights[1][1]]
            for i, ax in enumerate(a):
                if abs(ax) < 0.01:
                    axis = i
                    hasWeight = False
                    break
                
        if not hasWeight: # haven't moved yet. let's try something
            out = [0, 0]
            out[control] = random.randint(-10, 10) or 1
            self.learned[control][axis] += 1
            self.output(out[0], out[1])
        else:
            self.move_robot_smart(control)
        
    def move_robot_smart(self, control): # controller output
        out = [0, 0]
        for axis in (0, 1): # (x, y)
            out[control] += self.weights[control][axis] * self.get_delta(axis)
        self.output(out[0], out[1])
        
    def learn(self, before, after):
        print(self.last_output)
        lc = MAX_WEIGHT
        for axis in (0, 1):
            for control in (0, 1):
                delta = abs(after[axis]) - abs(before[axis])
                o = self.last_output[control]
                if p.target[axis] > self.robot.getPos()[axis]: o = -o
                if not abs(delta) == abs(self.last_output[control]): o = -abs(o)
                a = -self.learn_rate * (o * delta * PROGRAM_SPEED)
                self.weights[control][axis] += a
                self.weights[control][axis] = max(-lc, min(lc, self.weights[control][axis]))
        
    def output(self, x, y):
        mo = MAX_SPEED
        x = min(mo, max(-mo, x))
        y = min(mo, max(-mo, y))
        self.last_output = (x, y)
        self.robot.move(x, y)

def listen(c):
    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Absolute":
                if event.code == "ABS_X":
                    c.x = int(event.state) / 32768
                if event.code == "ABS_Y":
                    c.y = int(event.state) / 32768

class HumanGamepadController:
    def __init__(self, robot):
        self.robot = robot
        self.last_output = None
        self.x = 0
        self.y = 0
        self.lt = threading.Thread(target=listen, args=(self,))
        self.lt.setDaemon(True)
        self.lt.start()
    
    def get_delta(self, axis):
        """Returns a tuple."""
        return self.robot.getPos()[axis] - p.target[axis]
    
    def get_delta_total(self):
        return math.sqrt((self.robot.getPos()[0] - p.target[0])**2 + (self.robot.getPos()[1] - p.target[1])**2)
    
    def move_robot(self):
        self.output(self.x * 10, self.y * 10)
        
    def output(self, x, y):
        mo = MAX_SPEED
        x = min(mo, max(-mo, x))
        y = min(mo, max(-mo, y))
        self.last_output = (x, y)
        self.robot.move(x, y)
        
class HumanKeyboardController:
    def __init__(self, robot):
        self.robot = robot
        self.last_output = None
        self.ox = {
                   'a': -10,
                   'd': 10
                   }
        self.oy = {
                   'w': -10,
                   's': 10
                   }
    
    def get_delta(self, axis):
        """Returns a tuple."""
        return self.robot.getPos()[axis] - p.target[axis]
    
    def get_delta_total(self):
        return math.sqrt((self.robot.getPos()[0] - p.target[0])**2 + (self.robot.getPos()[1] - p.target[1])**2)
    
    def move_robot(self):
        k = p.win.checkKey()
        self.output(self.ox.get(k, 0), self.oy.get(k, 0))
        
    def output(self, x, y):
        mo = 10
        x = min(mo, max(-mo, x))
        y = min(mo, max(-mo, y))
        self.last_output = (x, y)
        self.robot.move(x, y)

def init():
    pass

def robot_init():
    p.win = GraphWin("2D Point ROBOT", X_MAX, Y_MAX, autoflush=False) #500x500 window
    #p.graphwin = GraphWin("Data", 500, 500, autoflush=False)
    
    p.targets = []
    p.robot_movements = []
    p.robot_outputs_x = []
    p.robot_outputs_y = []
    p.robot_deltas_x = []
    p.robot_deltas_y = []
    p.robot_targetticks = []
    
    t = Point(random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
    p.target = (t.x, t.y)
    p.targets.append(t)
    
    p.robot_starting_point = (random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
    p.robot = Robot(p.robot_starting_point[0], p.robot_starting_point[1])
    p.cont = Controller(p.robot)
    
    p.tc = Circle(t, 5) # put target somewhere random
    p.tc.draw(p.win)
    
    p.robot_score = 0
    
    
    #zero = Line(Point(0, 250), Point(500, 250))
    #zero.draw(p.graphwin)
    
    p.win.getMouse() # pause till click
    
def update_graphs():
    DELTA_X = 'green'
    DELTA_Y = 'yellow'
    OUT_X = 'red'
    OUT_Y = 'blue'
    ABS_DIST = 'purple'
    colors = (DELTA_X, DELTA_Y, OUT_X, OUT_Y, ABS_DIST)
    p.last_points = getattr(p, 'last_points', None) or [[], [], [], [], []] # [[dx], [dy], [ox], [oy]]
    p.datalines = getattr(p, 'datalines', None) or []
    for t in p.last_points:
        for po in t:
            po.move(-1, 0)
    for l in p.datalines:
        l.move(-1, 0)
        if l.getP2().x < 0: p.datalines.remove(l)
    p.last_points[0].append(Point(500, 250-p.cont.get_delta(0)))
    p.last_points[1].append(Point(500, 250-p.cont.get_delta(1)))
    p.last_points[2].append(Point(500, 250-p.cont.last_output[0]))
    p.last_points[3].append(Point(500, 250-p.cont.last_output[1]))
    p.last_points[4].append(Point(500, 500-p.cont.get_delta_total()))
    for i, t in enumerate(p.last_points):
        if len(t) > 1:
            li = Line(t[-2], t[-1])
            li.setFill(colors[i])
            li.draw(p.graphwin)
            p.datalines.append(li)
            
def robot_update_target(iteration):
    if p.cont.get_delta_total() < ON_TARGET:
        p.robot_targetticks.append(iteration)
        a = Point(random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
        p.targets.append(a)
        p.tc.move(a.x - p.target[0], a.y - p.target[1])
        p.target = (a.x, a.y)
        p.robot_score += 1
        if CONTROL_RANDOMIZATION:
            global CONTROL_MAP
            global CONTROL_FLIP
            CONTROL_MAP = [random.choice([-1, 1]), random.choice([-1, 1])] # randomize i/o
            CONTROL_FLIP = random.choice([True, False])
            p.cont.weights = [[0, 0], [0, 0]] # [[o1 on p1, o1 on p2], [o2 on p1, o2 on p2]]

def robot_loop(iteration):
    b = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    p.robot_movements.append(b) # append movement
    p.robot_deltas_x.append(p.cont.get_delta(0))
    p.robot_deltas_y.append(p.cont.get_delta(1))
    for control in (0, 1):
        before = (p.cont.get_delta(0), p.cont.get_delta(1))
        p.cont.move_robot(control)
        if iteration > 150: # give it 3 cycles to learn
            p.move_random(iteration)
        after = (p.cont.get_delta(0), p.cont.get_delta(1))
        p.cont.learn(before, after)
    a = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    p.robot_outputs_x.append(a.x - b.x)
    p.robot_outputs_y.append(a.y - b.y)
    l = Line(b, a)
    l.setFill('yellow')
    l.draw(p.win)
    
    print(p.cont.weights)
    #print(p.cont.get_delta(0), p.cont.get_delta(1))
    
    #update_graphs()
    
    robot_update_target(iteration)
    
    time.sleep(PROGRAM_SPEED)
    try:
        a = p.win.checkMouse()
        k = p.win.checkKey()
        if a:
            p.tc.move(a.x - p.target[0], a.y - p.target[1])
            p.target = (a.x, a.y)
        if k == 'r':
            p.robot.reverse = not p.robot.reverse
        if k == 'q':
            p.cont.weights = [[0, 0], [0, 0]]
            p.cont.learned = [[0, 0], [0, 0]]
        update()
    except GraphicsError:
        return False
    return iteration < 60*20 # 1 min

def reset():
    pass

def human_init():
    p.win = GraphWin("2D Point HUMAN", X_MAX, Y_MAX, autoflush=False) #500x500 window
    #p.graphwin = GraphWin("Data", 500, 500, autoflush=False)
    
    p.human_movements = []
    p.human_outputs_x = []
    p.human_outputs_y = []
    p.human_deltas_x = []
    p.human_deltas_y = []
    p.human_targetticks = []
    
    t = p.targets[0]
    p.target = (t.x, t.y)
    
    p.robot = Robot(p.robot_starting_point[0], p.robot_starting_point[1])
    try:
        get_gamepad()
    except UnpluggedError:
        p.cont = HumanKeyboardController(p.robot)
    else:
        p.cont = HumanGamepadController(p.robot)
    
    p.tc = Circle(t, 5) # put target somewhere random
    p.tc.draw(p.win)
    
    p.human_score = 0
    
    p.win.getMouse() # pause till click
    
def human_update_target(iteration):
    if p.cont.get_delta_total() < ON_TARGET:
        p.human_score += 1
        p.human_targetticks.append(iteration)
        try:
            a = p.targets[p.human_score]
        except: # whoa, the human is actually winning
            a = Point(random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
            p.targets.append(a)
        p.tc.move(a.x - p.target[0], a.y - p.target[1])
        p.target = (a.x, a.y)
        if CONTROL_RANDOMIZATION:
            global CONTROL_MAP
            global CONTROL_FLIP
            CONTROL_MAP = [random.choice([-1, 1]), random.choice([-1, 1])] # randomize i/o
            CONTROL_FLIP = random.choice([True, False])

def human_loop(iteration):
    b = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    p.human_movements.append(b) # append movement
    p.human_deltas_x.append(p.cont.get_delta(0))
    p.human_deltas_y.append(p.cont.get_delta(1))
    
    try:
        p.cont.move_robot()
    except GraphicsError:
        return False
        
    a = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    p.human_outputs_x.append(a.x - b.x)
    p.human_outputs_y.append(a.y - b.y)
    l = Line(b, a)
    l.setFill('yellow')
    l.draw(p.win)
    
    
    human_update_target(iteration)
    
    time.sleep(PROGRAM_SPEED)
    try:
        a = p.win.checkMouse()
        update()
    except GraphicsError:
        return False
    return iteration < 60*20 # 1 min

def output_data(include_human=True):
    t = datetime.today().isoformat()
    all_data = {}
    
    m = []
    for po in p.robot_movements:
        m.append([po.x, po.y])
        
    all_data['robot-movements'] = m
    
    out = {}
    out['outputs-x'] = p.robot_outputs_x
    out['outputs-y'] = p.robot_outputs_y
    out['deltas-x'] = p.robot_deltas_x
    out['deltas-y'] = p.robot_deltas_y
    
    all_data['robot-outdeltas'] = out
    all_data['robot-targetticks'] = p.robot_targetticks
    
    if include_human:
        m = []
        for po in p.human_movements:
            m.append([po.x, po.y])
            
        all_data['human-movements'] = m
        
        out = {}
        out['outputs-x'] = p.human_outputs_x
        out['outputs-y'] = p.human_outputs_y
        out['deltas-x'] = p.human_deltas_x
        out['deltas-y'] = p.human_deltas_y
        
        all_data['human-outdeltas'] = out
        all_data['human-targetticks'] = p.human_targetticks
        
        m = []
        for po in p.targets:
            m.append([po.x, po.y])
        
    all_data['targets'] = m
    
    all_data['difficulty'] = DIFFICULTY
    
    if not os.path.exists('data/'):
        os.makedirs('data/')
    
    time.sleep(1)
    
    name = t.replace(':', '-') + 'd' + str(DIFFICULTY) + ('robot' if not include_human else "")
    
    with open('data/' + name + '.json', mode='w+') as f:
        json.dump(all_data, f)
    
if __name__ == '__main__':
    init()
    
    robot_init()
    iteration = 0
    while robot_loop(iteration):
        iteration += 1
    if not 'nohuman' in sys.argv:
        reset()
            
        human_init()
        iteration = 0
        while human_loop(iteration):
            iteration += 1
            
        print("Robot score: " + str(p.robot_score))
        print("Human score: " + str(p.human_score))
        output_data()
        print("Data can be found in /data.")
        print("Please email the data to machinelearning@avrae.io!")
        print("You can review your run by running python3 review.py")
    else:
        output_data(False)
        