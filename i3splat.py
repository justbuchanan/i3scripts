#!/usr/bin/env python3
#
# github.com/justbuchanan/i3scripts
#
# This module provides a compact way to specify layouts for i3wm and launch the
# corresponding programs. Create a Workspace object with the containers and apps
# you want, then call launch().
#
# Here's an example program:
#
#   from i3splat import *
#   mydir = "~/src"
#   ws = Workspace("code", [
#       (0.5, chrome(["stackoverflow.com"])),
#       (0.5, Container(SPLITV, [
#           (0.7, Container(TABBED, [
#               (0.5, urxvt(wdir=mydir, command="vim file.txt")),
#               (0.5, sublime([mydir])),
#           ])),
#           (0.3, urxvt(wdir=mydir)),
#       ])
#   )])
#   ws.launch()
#
# Instead of calling launch(), you can also print out the i3 layout json
# representation for debugging purposes:
#
#   print(ws.serialize_i3layout())
#
# Customization:
#
# * This script is mostly independent of the other ones in this repository. You
#   will just need to modify or replace the Workspace.launch() method. See
#   comments in that method for more info.
#
# * This module provides functions for a few common apps, but you will likely
#   want to add your own. See the ones at the bottom of this file as examples.

import subprocess
import os
import json
import time
import shlex
import sys


class Node:
    def __init__(self):
        self.type = 'con'


# layout types
SPLITH = 'splith'
SPLITV = 'splitv'
STACKED = 'stacked'
TABBED = 'tabbed'


class Container(Node):
    def __init__(self, layout, nodes_and_percents):
        super().__init__()
        self.layout = layout
        self.nodes = _flatten_tuples(nodes_and_percents)


class App(Node):
    def __init__(self, xClass, xInstance=None, command=None):
        super().__init__()
        self.command = command

        self.swallows = [{'class': '^%s$' % xClass}]
        if xInstance != None:
            self.swallows[0]['instance'] = '^%s$' % xInstance


class Workspace:
    def __init__(self, name, nodes_and_percents):
        self.name = name
        self.nodes = _flatten_tuples(nodes_and_percents)

    # Main entry point.
    def launch(self):
        # Find an unused workspace number and jump to it.
        from new_workspace import new_workspace
        new_workspace()

        # Rename the new workspace. Note that you may want to remove this or
        # replace it with your own script if you're not also using the
        # autoname_workspaces script in this directory.
        from rename_workspace import rename_workspace
        rename_workspace(self.name)

        self.load_i3layout()
        self.run_apps()

    def iterate_apps(self):
        def _iterate_node(node):
            if isinstance(node, App):
                yield node
            else:
                for child in node.nodes:
                    yield from _iterate_node(child)

        for node in self.nodes:
            yield from _iterate_node(node)

    def serialize_i3layout(self):
        return '\n\n'.join([
            json.dumps(n, cls=WorkspaceJSONEncoder, indent=4)
            for n in self.nodes
        ])

    def load_i3layout(self):
        fname = "/tmp/i3layout.json"
        with open(fname, "w") as f:
            f.write(self.serialize_i3layout())

        subprocess.check_call(["i3-msg", "append_layout", fname])

    # If delay is provided, wait a small amount of time between each app launch
    # to give it time to load its window. This helps ensure that they get placed
    # in the appropriate containers for apps that can't be launched with a
    # custom instance name.
    def run_apps(self, delay=None):
        for app in self.iterate_apps():
            if app.command != None:
                app.command()
                if delay != None:
                    time.sleep(delay)


class WorkspaceJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, App):
            a = obj.__dict__.copy()
            # The 'command' property is used by this python program to launch
            # the app, but it doesn't go in the i3 layout file.
            del a['command']
            return a
        elif isinstance(obj, Container):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


# Flatten a list of (percent, Node) tuples to just [Node] with the percent
# property set on each.
def _flatten_tuples(pairs):
    nodes = []
    for p in pairs:
        n = p[1]
        n.percent = p[0]
        nodes.append(n)
    return nodes


# Apps
################################################################################


def _cmd(args):
    joined = ' '.join(args)
    print("$ %s" % joined)
    return lambda: subprocess.Popen(joined, shell=True)


# Note: specify the name property to ensure that i3 can uniquely match each one.
# Otherwise it's left up to chance that they launch windows in the order that
# they are called, which may not always be the case.
def urxvt(wdir="~", command=None, name="urxvt", interactive=True):
    shell = os.environ["SHELL"]

    wdir = os.path.expanduser(wdir)
    args = ["urxvt", "-cd", shlex.quote(wdir), "-name", name, "-e", shell]
    if command != None:
        args.append("-c")
        args.append(shlex.quote("%s; %s -i" % (command, shell)))

    return App(command=_cmd(args), xClass="URxvt", xInstance=name)


def chrome(urls):
    browser = ["google-chrome-stable", "--new-window"]
    return App(xClass="Google-chrome", command=_cmd(browser + urls))


def sublime(paths):
    quoted_paths = [shlex.quote(p) for p in paths]
    return App(command=_cmd(["subl", "-n"] + quoted_paths), xClass="Subl")
