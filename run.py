'''
Created on Jun 19, 2017

@author: andrew
'''

from datetime import datetime
import json
import math
import random

from inputs import get_gamepad, UnpluggedError, get_key

from lib.graphics import *


Y_MIN = 0
Y_MAX = 500
X_MIN = 0
X_MAX = 500

PROGRAM_SPEED = 1/20 # 20 tps

CONTROL_MAP = [random.choice([-1, 1]), random.choice([-1, 1])] # randomize i/o
CONTROL_FLIP = random.choice([True, False])

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
        self.learn_rate = 0.005
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
        lc = 1
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
        mo = 10
        x = min(mo, max(-mo, x))
        y = min(mo, max(-mo, y))
        self.last_output = (x, y)
        self.robot.move(x, y)
        
class HumanController:
    def __init__(self, robot):
        self.robot = robot
        self.last_output = None
    
    def get_delta(self, axis):
        """Returns a tuple."""
        return self.robot.getPos()[axis] - p.target[axis]
    
    def get_delta_total(self):
        return math.sqrt((self.robot.getPos()[0] - p.target[0])**2 + (self.robot.getPos()[1] - p.target[1])**2)
    
    def move_robot(self):
        events = get_gamepad()
        
    def output(self, x, y):
        mo = 10
        x = min(mo, max(-mo, x))
        y = min(mo, max(-mo, y))
        self.last_output = (x, y)
        self.robot.move(x, y)

def init():
    try:
        get_gamepad()
    except UnpluggedError:
        print("No gamepad detected, falling back to keyboard!")
        p.human_input = get_key
    else:
        p.human_input = get_gamepad

def robot_init():
    p.win = GraphWin("2D Point ROBOT", X_MAX, Y_MAX, autoflush=False) #500x500 window
    #p.graphwin = GraphWin("Data", 500, 500, autoflush=False)
    
    p.targets = []
    p.robot_movements = []
    p.robot_outputs_x = []
    p.robot_outputs_y = []
    p.robot_deltas_x = []
    p.robot_deltas_y = []
    
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
            
def update_target():
    if p.cont.get_delta_total() < 2:
        a = Point(random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
        p.targets.append(a)
        p.tc.move(a.x - p.target[0], a.y - p.target[1])
        p.target = (a.x, a.y)
        p.robot_score += 1

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
    
    update_target()
    
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
    
    t = p.targets[0]
    p.target = (t.x, t.y)
    
    p.robot = Robot(p.robot_starting_point[0], p.robot_starting_point[1])
    p.cont = HumanController(p.robot)
    
    p.tc = Circle(t, 5) # put target somewhere random
    p.tc.draw(p.win)
    
    p.human_score = 0
    
    p.win.getMouse() # pause till click

def human_loop(iteration):
    b = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    p.human_movements.append(b) # append movement
    p.human_deltas_x.append(p.cont.get_delta(0))
    p.human_deltas_y.append(p.cont.get_delta(1))
    
    p.cont.move_robot()
        
    a = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    p.human_outputs_x.append(a.x - b.x)
    p.human_outputs_y.append(a.y - b.y)
    l = Line(b, a)
    l.setFill('yellow')
    l.draw(p.win)
    
    
    update_target()
    
    time.sleep(PROGRAM_SPEED)
    try:
        a = p.win.checkMouse()
        update()
    except GraphicsError:
        return False
    return iteration < 60*20 # 1 min

def output_data():
    t = datetime.today().isoformat()
    with open('data/robot-movements-' + t + '.txt', mode='w') as f:
        m = []
        for po in p.robot_movements:
            m.append([po.x, po.y])
        f.write(json.dumps(m))
    with open('data/robot-outdeltas-' + t + '.txt', mode='w') as f:
        out = {}
        out['outputs-x'] = p.robot_outputs_x
        out['outputs-y'] = p.robot_outputs_y
        out['deltas-x'] = p.robot_deltas_x
        out['deltas-y'] = p.robot_deltas_y
        f.write(json.dumps(out))
    with open('data/human-movements-' + t + '.txt', mode='w') as f:
        pass
    with open('data/human-outdeltas-' + t + '.txt', mode='w') as f:
        pass
    
if __name__ == '__main__':
    init()
    
    robot_init()
    iteration = 0
    while robot_loop(iteration):
        iteration += 1
    
    reset()
        
    human_init()
    iteration = 0
    while human_loop(iteration):
        iteration += 1
        
    print("Robot score: " + str(p.robot_score))
    print("Human score: " + str(p.human_score))
    output_data()
    print("Data can be found in /data.")
        