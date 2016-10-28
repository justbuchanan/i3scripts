import re

# Used so that we can keep the workspace's name when we add icons to it.
# Returns a dictionary with the following keys: 'num', 'shortname', and 'icons'
# Any field that's missing in @name will be None in the returned dict
def parse_workspace_name(name):
    return re.match('(?P<num>\d+):?(?P<shortname>\w+)? ?(?P<icons>.+)?', name).groupdict()

# Given a dictionary with 'num', 'shortname', 'icons', return the formatted name
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
