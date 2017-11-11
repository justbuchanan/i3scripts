
# i3 Scripts

This repo contains a few scripts I've put together for i3.
Below is a description of the important ones.
See the script files themselves for more detailed info and instructions.

## autorename_workspaces.py

This script dynamically updates the i3 bar to show icons for running programs next to the workspace names.
It does this by listening for i3 window events and updating the workspace's "name".

In addition to showing program icons, it also renumbers i3 workspaces in ascending order.
This makes it easier to navigate.

Here's a [demo](https://gfycat.com/AfraidAmusingCoyote).


## new_workspace.py

Opens a new workspace on the current monitor, using the first available number.

## rename_workspace.py

Presents a small modal window with a text box that allows for renaming the current workspace.

## i3splat.py

This module provides a compact way to specify layouts for i3wm and launch the corresponding programs.
Create a `Workspace` object containing the containers and apps you want, then call `launch()`.
The specified layout will be loaded into i3, then the individual apps are launched in their places.
See the file itself for more detailed documentation.

Here's an example program:

~~~{.py}
from i3splat import *

mydir = "~/src"
ws = Workspace("code", [
    (0.5, chrome(["stackoverflow.com"])),
    (0.5, Container(SPLITV, [
        (0.7, Container(TABBED, [
            (0.5, urxvt(wdir=mydir, command="vim file.txt")),
            (0.5, sublime([mydir])),
        ])),
        (0.3, urxvt(wdir=mydir)),
    ])
)])
ws.launch()
~~~
