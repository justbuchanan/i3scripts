#!/usr/bin/env python3

# This script listens for i3 events and updates workspace names to show icons
# for running programs.  It contains icons for a few programs, but more can
# easily be added by inserting them into WINDOW_ICONS below.
#
# Dependencies
# * xorg-xprop - install through system package manager
# * i3ipc - install with pip
# * fontawesome - install with pip
#
# Installation:
# * Download this script and place it in ~/.config/i3/ (or anywhere you want)
# * Add "exec_always ~/.config/i3/i3-autoname-workspaces.py &" to your i3 config
# * Restart i3: "$ i3-msg restart"
#
# Configuration:
# The default i3 config's keybingings reference workspaces by name, which is an
# issue when using this script because the names are constantaly changing to
# show window icons.  Instead, you'll need to change the keybindings to
# reference workspaces by number.  Change lines like:
#   bindsym $mod+1 workspace 1
# To:
#   bindsym $mod+1 workspace number 1


import i3ipc
import subprocess as proc
import re
import signal
import sys
import fontawesome as fa

from util import *


# Add icons here for common programs you use.  The keys are the X window class
# (WM_CLASS) names and the icons can be any text you want to display. However
# most of these are character codes for font awesome:
#   http://fortawesome.github.io/Font-Awesome/icons/
# If you're not sure what the WM_CLASS is for your application, you can use
# xprop (https://linux.die.net/man/1/xprop). Run `xprop | grep WM_CLASS`
# then click on the application you want to inspect.
WINDOW_ICONS = {
    'urxvt': fa.icons['terminal'],
    'google-chrome': fa.icons['chrome'],
    'subl': fa.icons['file-text-o'],
    'subl3': fa.icons['file-text-o'],
    'spotify': fa.icons['music'], # could also use 'spotify' from font awesome
    'firefox': fa.icons['firefox'],
    'libreoffice': fa.icons['file-text-o'],
    'feh': fa.icons['picture-o'],
    'mupdf': fa.icons['file-pdf-o'],
    'evince': fa.icons['file-pdf-o'],
    'thunar': fa.icons['files-o'],
    'gpick': fa.icons['eyedropper'],
    'atom': fa.icons['code'],
    'steam': fa.icons['steam'],
    'zenity': fa.icons['window-maximize'],
}

# This icon is used for any application not in the list above
DEFAULT_ICON = '*'


i3 = i3ipc.Connection()


# Returns an array of the values for the given property from xprop.  This
# requires xorg-xprop to be installed.
def xprop(win_id, property):
    try:
        prop = proc.check_output(['xprop', '-id', str(win_id), property], stderr=proc.DEVNULL)
        prop = prop.decode('utf-8')
        return re.findall('"([^"]+)"', prop)
    except proc.CalledProcessError as e:
        print("Unable to get property for window '%d'" % win_id)
        return None

def icon_for_window(window):
    classes = xprop(window.window, 'WM_CLASS')
    if classes != None and len(classes) > 0:
        for cls in classes:
            cls = cls.lower() # case-insensitive matching
            if cls in WINDOW_ICONS:
                return WINDOW_ICONS[cls]
        print('No icon available for window with classes: %s' % str(classes))
    return DEFAULT_ICON

# renames all workspaces based on the windows present
def rename():
    for workspace in i3.get_tree().workspaces():
        name_parts = parse_workspace_name(workspace.name)
        name_parts['icons'] = ' '.join([icon_for_window(w) for w in workspace.leaves()])
        new_name = construct_workspace_name(name_parts)
        i3.command('rename workspace "%s" to "%s"' % (workspace.name, new_name))

rename()

# exit gracefully when ctrl+c is pressed
def signal_handler(signal, frame):
    # rename workspaces to just numbers and shortnames on exit to indicate that
    # this script is no longer running
    for workspace in i3.get_tree().workspaces():
        name_parts = parse_workspace_name(workspace.name)
        name_parts['icons'] = None
        new_name = construct_workspace_name(name_parts)
        i3.command('rename workspace "%s" to "%s"' % (workspace.name, new_name))
    i3.main_quit()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# call rename() for relevant window events
def on_change(i3, e):
    if e.change in ['new', 'close', 'move']:
        rename()
i3.on('window', on_change)
i3.main()
