#!/usr/bin/env python3

# This script listens for i3 events and updates workspace names to show icons
# for running programs.  It contains icons for a few programs, but more can
# easily be added by inserting them into WINDOW_ICONS below.
#
# Dependencies
# * xorg-xprop - install through system package manager
# * i3ipc - install with pip


import i3ipc
import subprocess as proc
import re


# Add icons here for common programs you use.  The keys are the X window class
# (WM_CLASS) names and the icons can be any text you want to display. However
# most of these are character codes for font awesome:
#   http://fortawesome.github.io/Font-Awesome/icons/
FA_CHROME = '\uf268'
FA_CODE = '\uf121'
FA_FILE_PDF_O = '\uf1c1'
FA_FILE_TEXT_O = '\uf0f6'
FA_FILES_O = '\uf0c5'
FA_FIREFOX = '\uf269'
FA_MUSIC = '\uf001'
FA_PICTURE_O = '\uf03e'
FA_SPOTIFY = '\uf1bc'
FA_TERMINAL = '\uf120'
WINDOW_ICONS = {
    'urxvt': FA_TERMINAL,
    'google-chrome': FA_CHROME,
    'subl': FA_CODE,
    'subl3': FA_CODE,
    'spotify': FA_MUSIC,
    'Firefox': FA_FIREFOX,
    'libreoffice': FA_FILE_TEXT_O,
    'feh': FA_PICTURE_O,
    'mupdf': FA_FILE_PDF_O,
    'evince': FA_FILE_PDF_O,
    'thunar': FA_FILES_O,
}


i3 = i3ipc.Connection()

# Returns an array of the values for the given property from xprop.  This
# requires xorg-xprop to be installed.
def xprop(win_id, property):
    try:
        prop = proc.check_output(['xprop', '-id', str(win_id), property], stderr=proc.DEVNULL)
        prop = prop.decode('utf-8')
        return re.findall('"([^"]+)"', prop)
    except proc.CalledProcessError as e:
        print("Unable to get property for window '%s'" % str(win_id))
        return None


def icon_for_window(window):
    classes = xprop(window.window, 'WM_CLASS')
    if classes != None and len(classes) > 0:
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
