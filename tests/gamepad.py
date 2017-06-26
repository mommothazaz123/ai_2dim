'''
Created on Jun 26, 2017

@author: andrew
'''

from __future__ import print_function

import time

from inputs import get_gamepad


def main():
    """Just print out some event infomation when the gamepad is used."""
    while 1:
        events = get_gamepad()
        for event in events:
            print(event.ev_type, event.code, event.state)
        time.sleep(1/20)


if __name__ == "__main__":
    main()