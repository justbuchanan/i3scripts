#!/usr/bin/env python3
#
# github.com/justbuchanan/i3scripts
#
# This script listens for i3 events and updates workspace names to show icons
# for running programs.  It contains icons for a few programs, but more can
# easily be added by editing the WINDOW_ICONS list below.
#
# It also re-numbers workspaces in ascending order with one skipped number
# between monitors (leaving a gap for a new workspace to be created). By
# default, i3 workspace numbers are sticky, so they quickly get out of order.
#
# Dependencies
# * xorg-xprop  - install through system package manager
# * i3ipc       - install with pip
# * https://github.com/ryanoasis/nerd-fonts - use install.sh
#
# Installation:
# * Download this repo and place it in ~/.config/i3/ (or anywhere you want)
# * Add "exec_always ~/.config/i3/i3scripts/autoname_workspaces.py &" to your i3 config
# * Restart i3: $ i3-msg restart
#
# Configuration:
# The default i3 config's keybindings reference workspaces by name, which is an
# issue when using this script because the "names" are constantly changing to
# include window icons.  Instead, you'll need to change the keybindings to
# reference workspaces by number.  Change lines like:
#   bindsym $mod+1 workspace 1
# To:
#   bindsym $mod+1 workspace number 1

import argparse
import i3ipc
import logging
import signal
import sys

from util import *

# Add icons here for common programs you use.  The keys are the X window class
# (WM_CLASS) names (lower-cased) and the icons can be any text you want to
# display.
#
# Most of these are character codes for nerd fonts:
#   https://github.com/ryanoasis/nerd-fonts
# Search on:
#   https://www.nerdfonts.com/cheat-sheet
#
# If you're not sure what the WM_CLASS is for your application, you can use
# xprop (https://linux.die.net/man/1/xprop). Run `xprop | grep WM_CLASS`
# then click on the application you want to inspect.
terminal = ''
code = ''
play = ''
cube = ''
copy = ''
file = ''
pdf = ''
mail = ''
image = ''
voice = '🎤'

WINDOW_ICONS = {
    'alacritty': terminal,
    'atom': '',
    'banshee': play,
    'blender': '',
    'chromium': '',
    'cura': cube,
    'darktable': image,
    'discord': 'ﭮ',
    'eclipse': '',
    'emacs': code,
    'eog': image,
    'evince': pdf,
    'evolution': mail,
    'feh': image,
    'file-roller': '',
    'filezilla': '',
    'firefox': '',
    'firefox-esr': '',
    'gimp-2.8': image,
    'gimp': image,
    'gnome-control-center': '',
    'gnome-terminal-server': terminal,
    'google-chrome': '',
    'brave-browser': '爵',
    'gpick': '',
    'imv': image,
    'java': '',
    'jetbrains-idea': code,
    'jetbrains-studio': code,
    'keepassxc': '',
    'keybase': '',
    'kicad': '',
    'kitty': terminal,
    'libreoffice': file,
    'lua5.1': '',
    'mpv': '',
    'mupdf': pdf,
    'mysql-workbench-bin': '',
    'nautilus': copy,
    'nemo': copy,
    'openscad': cube,
    'pavucontrol': '🔊',
    'postman': '',
    'rhythmbox': play,
    'robo3t': '',
    'slack': '',
    'slic3r.pl': cube,
    'spotify': '',
    'steam': '',
    'subl': file,
    'subl3': file,
    'sublime_text': file,
    'thunar': copy,
    'thunderbird': mail,
    'totem': play,
    'urxvt': terminal,
    'xfce4-terminal': terminal,
    'xournal': file,
    'yelp': code,
    'zenity': '',
    'zoom': '',
    'feh': '',
    'lutris': '',
    'code': '',
    'ts3client_linux_amd64': voice,
    'TeamSpeak': voice,
    'mumble': voice,
    'skype' : '', 
    'Wine': '',
    'anydesk': '',
    'obs': '辶',
    'termite': terminal,
    'insomnia': 'ﭧ',
    'simplenote': '',
    'Godot': code,
    'lbry': ''
}

# This icon is used for any application not in the list above
DEFAULT_ICON = ''

# Global setting that determines whether workspaces will be automatically
# re-numbered in ascending order with a "gap" left on each monitor. This is
# overridden via command-line flag.
RENUMBER_WORKSPACES = True


def ensure_window_icons_lowercase():
    global WINDOW_ICONS
    WINDOW_ICONS = {name.lower(): icon for name, icon in WINDOW_ICONS.items()}


def icon_for_window(window):
    # Try all window classes and use the first one we have an icon for
    classes = xprop(window.window, 'WM_CLASS')
    if classes != None and len(classes) > 0:
        for cls in classes:
            cls = cls.lower()  # case-insensitive matching
            if cls in WINDOW_ICONS:
                return WINDOW_ICONS[cls]
    logging.info(
        'No icon available for window with classes: %s' % str(classes))
    return DEFAULT_ICON


# renames all workspaces based on the windows present
# also renumbers them in ascending order, with one gap left between monitors
# for example: workspace numbering on two monitors: [1, 2, 3], [5, 6]
def rename_workspaces(i3, icon_list_format='default'):
    ws_infos = i3.get_workspaces()
    prev_output = None
    n = 1
    for ws_index, workspace in enumerate(i3.get_tree().workspaces()):
        ws_info = ws_infos[ws_index]

        name_parts = parse_workspace_name(workspace.name)
        icon_list = [icon_for_window(w) for w in workspace.leaves()]
        new_icons = format_icon_list(icon_list, icon_list_format)

        # As we enumerate, leave one gap in workspace numbers between each monitor.
        # This leaves a space to insert a new one later.
        if ws_info.output != prev_output and prev_output != None:
            n += 1
        prev_output = ws_info.output

        # optionally renumber workspace
        new_num = n if RENUMBER_WORKSPACES else name_parts.num
        n += 1

        new_name = construct_workspace_name(
            NameParts(
                num=new_num, shortname=name_parts.shortname, icons=new_icons))
        if workspace.name == new_name:
            continue
        i3.command(
            'rename workspace "%s" to "%s"' % (workspace.name, new_name))


# Rename workspaces to just numbers and shortnames, removing the icons.
def on_exit(i3):
    for workspace in i3.get_tree().workspaces():
        name_parts = parse_workspace_name(workspace.name)
        new_name = construct_workspace_name(
            NameParts(
                num=name_parts.num, shortname=name_parts.shortname,
                icons=None))
        if workspace.name == new_name:
            continue
        i3.command(
            'rename workspace "%s" to "%s"' % (workspace.name, new_name))
    i3.main_quit()
    sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=
        "Rename workspaces dynamically to show icons for running programs.")
    parser.add_argument(
        '--norenumber_workspaces',
        action='store_true',
        default=False,
        help=
        "Disable automatic workspace re-numbering. By default, workspaces are automatically re-numbered in ascending order."
    )
    parser.add_argument(
        '--icon_list_format',
        type=str,
        default='default',
        help=
        "The formatting of the list of icons."
        "Accepted values:"
        "    - default: no formatting,"
        "    - mathematician: factorize with superscripts (e.g. aababa -> a⁴b²),"
        "    - chemist: factorize with subscripts (e.g. aababa -> a₄b₂)."
    )
    args = parser.parse_args()

    RENUMBER_WORKSPACES = not args.norenumber_workspaces

    logging.basicConfig(level=logging.INFO)

    ensure_window_icons_lowercase()

    i3 = i3ipc.Connection()

    # Exit gracefully when ctrl+c is pressed
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda signal, frame: on_exit(i3))

    rename_workspaces(i3, icon_list_format=args.icon_list_format)

    # Call rename_workspaces() for relevant window events
    def event_handler(i3, e):
        if e.change in ['new', 'close', 'move']:
            rename_workspaces(i3, icon_list_format=args.icon_list_format)

    i3.on('window', event_handler)
    i3.on('workspace::move', event_handler)
    i3.main()
