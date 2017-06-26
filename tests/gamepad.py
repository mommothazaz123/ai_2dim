'''
Created on Jun 26, 2017

@author: andrew
'''

from __future__ import print_function

import time

from inputs import get_gamepad, devices


def main():
    """Just print out some event infomation when the gamepad is used."""
    iteration = 0
    while 1:
        events = iter(devices.gamepads[0])
        for event in events:
            print(event.ev_type, event.code, event.state)
        iteration += 1
        print(iteration)


if __name__ == "__main__":
    main()