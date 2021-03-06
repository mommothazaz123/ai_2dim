'''
Created on Jun 26, 2017

@author: andrew
'''

from __future__ import print_function

import threading
import time

from lib.inputs import get_gamepad, devices


def main():
    """Just print out some event infomation when the gamepad is used."""
    iteration = 0
    devices.gamepads[0].read_size = 5
    while 1:
        events = iter(devices.gamepads[0])
        e = next(events)
        while e:
            print(e)
            for event in e:
                print(event.ev_type, event.code, event.state)
            e = next(events)
        iteration += 1
        print(iteration)
        
def main2():
    """Just print out some event infomation when the gamepad is used."""
    devices.gamepads[0].read_size = 5
    iteration = 0
    while 1:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)
        time.sleep(1)
        iteration += 1
        print(iteration)

def listen():
    iteration = 0
    while 1:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)
        time.sleep(1)
        iteration += 1
        print(iteration)


def main3():
    lt = threading.Thread(target=listen)
    lt.setDaemon(True)
    lt.start()


if __name__ == "__main__":
    main2()