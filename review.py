'''
Created on Jun 23, 2017

@author: andrew
'''
import glob
import json
import time

from lib.graphics import GraphWin, Point, Line, Circle, Text


class Program():
    pass

p = Program()

COLORS = {
          'human_path': 'green',
          'robot_path': 'red'
          }

def select_file():
    files = glob.glob('data/*.json')
    out = ""
    for i, file in enumerate(sorted(files)):
        out += "[{}]: {}\n".format(i, file)
    print(out)
    selected_file = int(input("Input file number: "))
    with open(files[selected_file], mode='r') as f:
        return json.load(f)
    
def initialize_window():
    p.win = GraphWin("Data Review", 500, 500)
    p.i = []
    p.i2 = []
    
def draw_targets():
    points = [Point(_[0], _[1]) for _ in p.data['targets']]
    for i, po in enumerate(points):
        t = Text(po, str(i))
        t.draw(p.win)
        p.i.append(t)
    
def draw_robot_path():
    points = [Point(_[0], _[1]) for _ in p.data['robot-movements']]
    for i, po in enumerate(points[:-2]):
        l = Line(po, points[i+1])
        l.setFill(COLORS['robot_path'])
        l.draw(p.win)
        p.i.append(l)

def draw_human_path():
    points = [Point(_[0], _[1]) for _ in p.data['human-movements']]
    for i, po in enumerate(points[:-2]):
        l = Line(po, points[i+1])
        l.setFill(COLORS['human_path'])
        l.draw(p.win)
        p.i.append(l)
        
def clear():
    for i in p.i:
        i.undraw()

def step_thru_path():
    rpoints = [Point(_[0], _[1]) for _ in p.data['robot-movements']]
    hpoints = [Point(_[0], _[1]) for _ in p.data['human-movements']]
    rtts = p.data['robot-targetticks']
    htts = p.data['human-targetticks']
    index = 0
    robot_next = 0
    human_next = 0
    while index < max(len(htts), len(rtts)):
        p.win.getMouse()
        for i in p.i2:
            i.undraw()
        try:
            robot_last = robot_next
            robot_next = rtts[index]
        except IndexError:
            robot_next = None
        
        try:
            human_last = human_next
            human_next = htts[index]
        except IndexError:
            human_next = None
        
        if robot_next is not None:
            rpts = rpoints[robot_last:robot_next]
            for i, po in enumerate(rpts[:-2]):
                l = Line(po, rpts[i+1])
                l.setFill(COLORS['robot_path'])
                l.draw(p.win)
                p.i2.append(l)
                time.sleep(1/20)
        if human_next is not None:
            hpts = hpoints[human_last:human_next]
            for i, po in enumerate(hpts[:-2]):
                l = Line(po, hpts[i+1])
                l.setFill(COLORS['human_path'])
                l.draw(p.win)
                p.i2.append(l)
                time.sleep(1/20)
        index += 1

if __name__ == '__main__':
    p.data = select_file()
    print(p.data)
    initialize_window()
    draw_targets()
    
    p.win.getMouse()
    
    draw_robot_path()
    draw_human_path()
    
    p.win.getMouse()
    
    clear()
    
    draw_targets()
    
    step_thru_path()
    
    
    
    
    