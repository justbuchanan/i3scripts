
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
