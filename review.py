'''
Created on Jun 23, 2017

@author: andrew
'''
import glob
import json

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
    for i, file in enumerate(files):
        out += "[{}]: {}\n".format(i, file)
    print(out)
    selected_file = int(input("Input file number: "))
    with open(files[selected_file], mode='r') as f:
        return json.load(f)
    
def initialize_window():
    p.win = GraphWin("Data Review", 500, 500)
    
def draw_targets():
    points = [Point(_[0], _[1]) for _ in p.data['targets']]
    for i, po in enumerate(points):
        t = Text(po, str(i))
        t.draw(p.win)
    
def draw_robot_path():
    points = [Point(_[0], _[1]) for _ in p.data['robot-movements']]
    for i, po in enumerate(points[:-2]):
        l = Line(po, points[i+1])
        l.setFill(COLORS['robot_path'])
        l.draw(p.win)

def draw_human_path():
    points = [Point(_[0], _[1]) for _ in p.data['human-movements']]
    for i, po in enumerate(points[:-2]):
        l = Line(po, points[i+1])
        l.setFill(COLORS['human_path'])
        l.draw(p.win)

if __name__ == '__main__':
    p.data = select_file()
    print(p.data)
    initialize_window()
    draw_targets()
    
    p.win.getMouse()
    
    draw_robot_path()
    draw_human_path()
    
    p.win.getMouse()