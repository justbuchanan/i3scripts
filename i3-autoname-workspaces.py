#!/usr/bin/env python3

# This script listens for i3 events and updates workspace names to show icons
# for running programs.

import i3ipc
import subprocess as proc
import re


# Add icons here for common programs you use.  The keys are the X window class
# names and the icons can be any text you want to display. However most of
# these are character codes for font awesome:
#   http://fortawesome.github.io/Font-Awesome/icons/
WINDOW_ICONS = {
    'urxvt': '\uf120',
    'google-chrome': '\uf268',
    'subl': '\uf1c9',
    'subl3': '\uf1c9',
    'spotify': '\uf001',
    'Firefox': '\uf269',
    'libreoffice': '\uf0f6',
    'feh': '\uf03e',
    'mupdf': '\uf1c1',
    'evince': '\uf1c1',
}


i3 = i3ipc.Connection()

# Returns an array of the values for the given property from xprop.  This
# requires xorg-xprop to be installed.
def xprop(win_id, property):
    try:
        prop = proc.check_output(['xprop', '-id', str(win_id), property])
        prop = prop.decode('utf-8')
        return re.findall('"([^"]+)"', prop)
    except proc.CalledProcessError as e:
        print("Unable to get property for window %" % str(win_id))
        return None


def icon_for_window(window):
    classes = xprop(window.window, 'WM_CLASS')
    for cls in classes:
        if cls in WINDOW_ICONS:
            return WINDOW_ICONS[cls]
    print('No icon available for window with classes: %s' % str(classes))
    return '*'

# renames all workspaces based on the windows present
def rename():
    for workspace in i3.get_tree().workspaces():
        icons = [icon_for_window(w) for w in workspace.leaves()]
        new_name = "%d: %s" % (workspace.num, '  '.join(icons))
        i3.command('rename workspace "%s" to "%s"' % (workspace.name, new_name))

rename()

# call rename() for relevant window events
def on_change(i3, e):
    if e.change in ['new', 'close', 'move']:
        rename()
i3.on('window', on_change)
i3.main()
