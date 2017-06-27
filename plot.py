'''
Created on Jun 27, 2017

@author: andrew
'''
import glob
import json
import sys

import plotly.graph_objs as go
import plotly.plotly as py


class Program:
    pass

p = Program()

def select_file():
    files = glob.glob('data/*.json')
    out = ""
    for i, file in enumerate(sorted(files)):
        out += "[{}]: {}\n".format(i, file)
    print(out)
    selected_file = int(input("Input file number: "))
    p.f = files[selected_file]
    with open(files[selected_file], mode='r') as f:
        return json.load(f)
    
def plot(data, nohuman=False):
    routdeltas = data['robot-outdeltas']
    
    rdeltasx = routdeltas['deltas-x']
    robot_deltas_x = go.Scatter(
        x = list(range(len(rdeltasx))),
        y = rdeltasx,
        name = "Robot Delta-X"
    )
    
    rdeltasy = routdeltas['deltas-y']
    robot_deltas_y = go.Scatter(
        x = list(range(len(rdeltasy))),
        y = rdeltasy,
        name = "Robot Delta-Y"
    )
    
    routsx = routdeltas['outputs-x']
    robot_outputs_x = go.Scatter(
        x = list(range(len(routsx))),
        y = routsx,
        name = "Robot Out X"
    )
    
    routsy = routdeltas['outputs-y']
    robot_outputs_y = go.Scatter(
        x = list(range(len(routsy))),
        y = routsy,
        name = "Robot Out Y"
    )
    
    if not nohuman:
        houtdeltas = data['human-outdeltas']
        
        hdeltasx = houtdeltas['deltas-x']
        human_deltas_x = go.Scatter(
            x = list(range(len(hdeltasx))),
            y = hdeltasx,
            name = "Human Delta-X"
        )
        
        hdeltasy = houtdeltas['deltas-y']
        human_deltas_y = go.Scatter(
            x = list(range(len(hdeltasy))),
            y = hdeltasy,
            name = "Human Delta-Y"
        )
        
        houtsx = houtdeltas['outputs-x']
        human_outputs_x = go.Scatter(
            x = list(range(len(houtsx))),
            y = houtsx,
            name = "Human Out X"
        )
        
        houtsy = houtdeltas['outputs-y']
        human_outputs_y = go.Scatter(
            x = list(range(len(houtsy))),
            y = houtsy,
            name = "Human Out Y"
        )
        
        data = [robot_deltas_x, robot_deltas_y, robot_outputs_x, robot_outputs_y,
                human_deltas_x, human_deltas_y, human_outputs_x, human_outputs_y]
    else:
        data = [robot_deltas_x, robot_deltas_y, robot_outputs_x, robot_outputs_y]
    
    py.iplot(data, filename='AIDATA ' + p.f.split('/')[-1])
    
if __name__ == '__main__':
    data = select_file()
    plot(data, 'nohuman' in sys.argv)