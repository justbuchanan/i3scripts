#!/usr/bin/env python3

import i3ipc
import subprocess as proc
import re

i3 = i3ipc.Connection()

def xprop(win_id, property):
    # note: requires xorg-xprop to be installed
    prop = proc.check_output(['xprop', '-id', str(win_id), property])
    prop = prop.decode('utf-8')
    m = re.match('[^\=]+\= "([^\n"]+)', prop)
    prop = m.group(1)
    return prop

def icon_for_window(window):
    icons = {
        'urxvt': '\uf120',
        'google-chrome': '\uf268',
        'subl': '\uf1c9'
    }
    cls = xprop(window.window, 'WM_CLASS')
    return icons[cls] if cls in icons else '*'

def rename():
    for workspace in i3.get_tree().workspaces():
        icons = [icon_for_window(w) for w in workspace.leaves()]

        new_name = str(workspace.num) + ': ' + '  '.join(icons)
        i3.command('rename workspace "%s" to "%s"' % (workspace.name, new_name))

def on_change(i3, e):
    if e.change in ['new', 'close', 'move']:
        rename()

rename()
i3.on('window', on_change)
i3.main()
