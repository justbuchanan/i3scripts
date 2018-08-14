#!/usr/bin/env python3
#
# github.com/justbuchanan/i3scripts
#
# This script is used to dynamically rename workspaces in i3. When run, it
# presents a text field popup using zenity, in which you can type a new name for
# the workspace. It is compatible with the autoname_workspaces script and
# renames only the "shortname" of the workspace, keeping the number and window
# icons in place.
#
# Note that this script can be used without autoname_workspaces.py.
#
# Dependencies:
# * zenity - install with system package manager
# * i3ipc  - install with pip

import i3ipc
import logging
import subprocess as proc
import sys

from util import *


def show_name_dialog(current_shortname):
    try:
        # use zenity to show a text box asking the user for a new workspace name
        prompt_title = "Rename Workspace:" if current_shortname == None \
                            else "Rename Workspace '%s':" % current_shortname
        response = proc.check_output(
            ['zenity', '--entry', "--text={}".format(prompt_title)])
        new_shortname = response.decode('utf-8').strip()
        logging.info("New name from user: '%s'" % new_shortname)

        # validate or fail
        if ' ' in new_shortname:
            msg = "No spaces allowed in workspace names"
            logging.error(msg)
            proc.check_call(['zenity', '--error', '--text=%s' % msg])
            sys.exit(1)

        return new_shortname

    except proc.CalledProcessError as e:
        logging.info("Cancelled by user, exiting...")
        sys.exit(1)


# If new_shortname is None, shows a zenity dialog asking for a new name
def rename_workspace(new_shortname=None):
    logging.basicConfig(level=logging.INFO)

    i3 = i3ipc.Connection()
    workspace = focused_workspace(i3)
    name_parts = parse_workspace_name(workspace.name)
    logging.info("Current workspace shortname: '%s'" % name_parts.shortname)

    # If name is not specified as a command line arg, ask the user.
    if new_shortname is None:
        new_shortname = show_name_dialog(name_parts.shortname)

    # get the current workspace and rename it
    new_name = construct_workspace_name(
        NameParts(
            num=name_parts.num,
            shortname=new_shortname,
            icons=name_parts.icons))
    workspace = focused_workspace(i3)
    res = i3.command(
        'rename workspace "%s" to "%s"' % (workspace.name, new_name))
    assert res[0]['success'], "Failed to rename workspace"


if __name__ == '__main__':
    new_shortname = sys.argv[1] if len(sys.argv) > 1 else None
    rename_workspace(new_shortname)
