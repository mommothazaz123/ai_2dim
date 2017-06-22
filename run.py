'''
Created on Jun 19, 2017

@author: andrew
'''

import random

from lib.graphics import *
import math


Y_MIN = 0
Y_MAX = 500
X_MIN = 0
X_MAX = 500

PROGRAM_SPEED = 1/20 # 20 tps

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
        if self.reverse:
            dx = -dx
            dy = -dy
        super().move(dx, dy)
        
class Controller:
    """This object should take input from the Robot and minimise delta."""
    def __init__(self, robot):
        self.robot = robot
        self.weights = [[0, 0], [0, 0]] # [[o1 on p1, o1 on p2], [o2 on p1, o2 on p2]]
        self.learned = [[0, 0], [0, 0]]
        self.learn_rate = 0.0005
        self.old_learn = self.learn_rate
        self.learn_rate_rate = 0.01
        self.last_output = None
        self.last_lr_output = 0
    
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
        lc = 5
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
        x = min(10, max(-10, x))
        y = min(10, max(-10, y))
        self.last_output = (x, y)
        self.robot.move(x, y)
        
    def change_learn(self):
        out = random.randint(-5, 5) * self.get_delta_total() / 100000
        self.last_lr_output += out
        self.learn_rate += out
        self.learn_rate = max(0, min(0.5, self.learn_rate))
        
    def learn_to_learn(self, before, after):
        delta = abs(after) - abs(before)
        if delta == 0: delta += 0.01
        self.learn_rate = (self.old_learn) + -self.learn_rate_rate * (self.last_lr_output * delta * (PROGRAM_SPEED*10))
        self.learn_rate = max(0, min(0.5, self.learn_rate))
        self.old_learn = self.learn_rate
        self.last_lr_output = 0

def init():
    p.win = GraphWin("2D Point", X_MAX, Y_MAX, autoflush=False) #500x500 window
    #p.graphwin = GraphWin("Data", 500, 500, autoflush=False)
    t = Point(random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
    p.target = (t.x, t.y)
    
    p.robot = Robot(random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
    p.cont = Controller(p.robot)
    
    p.tc = Circle(t, 5) # put target somewhere random
    p.tc.draw(p.win)
    
    p.score = 0
    
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
        p.tc.move(a.x - p.target[0], a.y - p.target[1])
        p.target = (a.x, a.y)
        p.score += 1

def loop(iteration):
    b = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    for control in (0, 1):
        before = (p.cont.get_delta(0), p.cont.get_delta(1))
        p.cont.move_robot(control)
        if iteration > 150: # give it 3 cycles to learn
            p.move_random(iteration)
        after = (p.cont.get_delta(0), p.cont.get_delta(1))
        p.cont.learn(before, after)
    a = Point(p.robot.getPos()[0], p.robot.getPos()[1])
    l = Line(b, a)
    l.draw(p.win)
    
    #print(p.cont.learn_rate)
    #if iteration > 10:
        #p.cont.change_learn()
            
        #if iteration % 200:
            #p.cont.learn_to_learn(p.before_ten, p.cont.get_delta_total())
            #p.before_ten = p.cont.get_delta_total()
    
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

if __name__ == '__main__':
    init()
    iteration = 0
    while loop(iteration):
        iteration += 1