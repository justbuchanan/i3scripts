import re
import logging
import subprocess as proc

# https://github.com/justbuchanan/i3scripts


def focused_workspace(i3):
    return [w for w in i3.get_workspaces() if w.focused][0]


# Takes a workspace 'name' from i3 and splits it into three parts:
# * 'num'
# * 'shortname' - the workspace's name, assumed to have no spaces
# * 'icons' - the string that comes after the
# Any field that's missing will be None in the returned dict
def parse_workspace_name(name):
    return re.match('(?P<num>\d+):?(?P<shortname>\w+)? ?(?P<icons>.+)?',
                    name).groupdict()


# Given a dictionary with 'num', 'shortname', 'icons', returns the formatted name
# by concatenating them together.
def construct_workspace_name(parts):
    new_name = str(parts['num'])
    if parts['shortname'] or parts['icons']:
        new_name += ':'

        if parts['shortname']:
            new_name += parts['shortname']

        if parts['icons']:
            new_name += ' ' + parts['icons']

    return new_name


# Return an array of values for the X property on the given window.
# Requires xorg-xprop to be installed.
def xprop(win_id, property):
    try:
        prop = proc.check_output(
            ['xprop', '-id', str(win_id), property], stderr=proc.DEVNULL)
        prop = prop.decode('utf-8')
        return re.findall('"([^"]+)"', prop)
    except proc.CalledProcessError as e:
        logging.warn("Unable to get property for window '%d'" % win_id)
        return None
