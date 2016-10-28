#!/usr/bin/env python3

## This script is used to dynamically rename workspace names in i3.
# When run, it presents a text field popup using zenity, in which you can type a
# new name for the workspace. It is compatible with the i3-autoname-workspaces
# script and renames only the "shortname" of the workspace, keeping the number
# and window icons in place.
#
# Note that this script can be used without i3-autoname-workspaces.py
#
# Dependencies:
# * zenity - install with system package manager
# * i3ipc - install with pip

import i3ipc
import logging
import subprocess as proc
import re
import sys

from util import *


logging.basicConfig(level=logging.INFO)

i3 = i3ipc.Connection()
workspace = [w for w in i3.get_workspaces() if w.focused][0]
name_parts = parse_workspace_name(workspace.name)
logging.info("Current workspace shortname: '%s'" % name_parts['shortname'])

try:
    # use zenity to show a text box asking the user for a new workspace name
    prompt_title = "Rename Workspace:" if name_parts['shortname'] == None else "Rename Workspace '%s':" % name_parts['shortname']
    response = proc.check_output(['zenity', '--entry', "--text=%s" % prompt_title])
    new_shortname = response.decode('utf-8').strip()
    logging.info("New name from user: '%s'" % new_shortname)

    if ' ' in new_shortname:
        msg = "No spaces allowed in workspace names"
        logging.error(msg)
        proc.check_call(['zenity', '--error', '--text=%s' % msg])
        sys.exit(1)

except proc.CalledProcessError as e:
    logging.info("Cancelled by user, exiting...")

name_parts['shortname'] = new_shortname
new_name = construct_workspace_name(name_parts)

# get the current workspace and rename it
workspace = [w for w in i3.get_workspaces() if w.focused][0]
res = i3.command('rename workspace "%s" to "%s"' % (workspace.name, new_name))
