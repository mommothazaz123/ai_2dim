'''
Created on Jun 26, 2017

@author: andrew
'''

from __future__ import print_function

import time

from inputs import get_gamepad


def main():
    """Just print out some event infomation when the gamepad is used."""
    iteration = 0
    while 1:
        events = get_gamepad()
        while events:
            for event in events:
                print(event.ev_type, event.code, event.state)
            events = get_gamepad()
        time.sleep(1)
        iteration += 1
        print(iteration)


if __name__ == "__main__":
    main()