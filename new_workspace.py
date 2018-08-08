#!/usr/bin/env python3
#
# github.com/justbuchanan/i3scripts

import i3ipc
import argparse
import logging
from util import *


# Finds the smallest workspace number such that it will open to the right of the
# existing workspaces on the current monitor. For example if the current monitor
# has workspace numbers [1,3,4], this function will return 5.
def find_next_ws_num_on_monitor(i3):
    focused_monitor = focused_workspace(i3).output
    logging.info('focused monitor: %s' % focused_monitor)

    ws_on_monitor = filter(lambda ws: ws['output'] == focused_monitor,
                           i3.get_workspaces())
    nums = [ws['num'] for ws in ws_on_monitor]
    maxnum = max(nums)
    logging.info('max workspace on monitor: %s' % str(maxnum))

    return maxnum + 1


def new_workspace(move_focused=False):
    i3 = i3ipc.Connection()
    new_ws_num = find_next_ws_num_on_monitor(i3)
    if move_focused:
        # move focused window the next open workspace
        i3.command('move window to workspace number {0}; workspace {0}'.format(
            new_ws_num))
    else:
        i3.command('workspace %d' % new_ws_num)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
        Jump to a new workspace to the right of the existing ones on the current  monitor."""
                                     )
    parser.add_argument(
        '--move_focused',
        '-m',
        action='store_true',
        help="Also bring the currently-focused window to this new workspace.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    new_workspace(args.move_focused)
