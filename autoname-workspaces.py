#!/usr/bin/env python3

# This script listens for i3 events and updates workspace names to show icons
# for running programs.

import i3ipc
import subprocess as proc
import re

i3 = i3ipc.Connection()

def xprop(win_id, property):
    # note: requires xorg-xprop to be installed
    try:
        prop = proc.check_output(['xprop', '-id', str(win_id), property])
        prop = prop.decode('utf-8')
        m = re.match('[^\=]+\= "([^\n"]+)', prop)
        prop = m.group(1)
        return prop
    except proc.CalledProcessError as e:
        print("Unable to get property for window %" % str(win_id))


def icon_for_window(window):
    # add icons to this list for common programs you use
    icons = {
        'urxvt': '\uf120',
        'google-chrome': '\uf268',
        'subl': '\uf1c9'
    }
    cls = xprop(window.window, 'WM_CLASS')
    return icons[cls] if cls in icons else '*'

# renames all workspaces based on the windows present
def rename():
    for workspace in i3.get_tree().workspaces():
        icons = [icon_for_window(w) for w in workspace.leaves()]

        new_name = str(workspace.num) + ': ' + '  '.join(icons)
        i3.command('rename workspace "%s" to "%s"' % (workspace.name, new_name))

rename()

# call rename() for relevant window events
def on_change(i3, e):
    if e.change in ['new', 'close', 'move']:
        rename()
i3.on('window', on_change)
i3.main()
