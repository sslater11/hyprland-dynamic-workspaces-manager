# Hyprland Dynamic Workspaces Manager Script 
I prefer being able to give each workspace a name, instead of the default assigned workspace numbers.
This script allows me to create workspaces on the fly, name them and switch between them with ease.

# Features
- Create a workspace with any name that you want.
- Rename a workspace.
- Move a window to any workspace.
- Switch to any window.

https://github.com/sslater11/hyprland-dynamic-workspaces-manager/assets/43177940/47113bd3-9059-48d1-b643-9804b615ac2f

# Dependencies:
- python3
- hyprctl - This should be installed with Hyprland
-  - The wayland fork by lbonn found at https://github.com/lbonn/rofi.git
  - rofi is used for the popup to list all workspaces/windows, and to handle all user input.
  - You can edit the script to change it to any other app launcher you prefer.
  - Please see this link for recommended app launchers that may work with this script.
  - https://wiki.hyprland.org/Useful-Utilities/App-Launchers/

## Why does it require rofi(the wayland fork) instead of wofi?
- Rofi has more features than wofi.
- Rofi can select a line in our list.
  - This is used when we display a list of workspaces. Our current workspace will be highlighted.
- Rofi can auto-select an item from the filtered list.
  - As we type and land on the last option, it will select it without us needing to press enter. I've disabled this by default, but it can be enabled in the script by changing the variable at the start of the script `auto_select = True`.


# Installation
## Install dependencies
- The rofi wayland fork found here.
  - https://github.com/lbonn/rofi.git
- Arch users use AUR package rofi-lbonn-wayland-only-git
  - https://aur.archlinux.org/packages/rofi-lbonn-wayland-only-git

- install python3 using your package manager

Download this script
```
cd ~/.config/hypr/
git clone https://github.com/sslater11/hyprland-dynamic-workspaces-manager.git
cd hyprland-dynamic-workspaces-manager/
chmod +x hyprland-dynamic-workspaces-manager.py
./hyprland-dynamic-workspaces-manager.py
```
See below for how to add this script to your Hyprland config.

# Usecase
I often group my windows by the project that I'm working on. I do this by placing them on a workspace with a name related to the project.

Sometimes things get disorganised and I forget which workspace I moved a window to. Having the app switcher allows me to type in the name of a window and jump straight to it.

I often run about 5+ different workspaces with several different programs. I try to keep everything open as it saves time later on when resuming a project.

Renaming workspaces is required as a things can become disorganised quickly.

I have heard that people like to keep a single workspace for their web browser, but this doesn't work for me. I often have multiple web browser windows with lots of tabs open too. I will have one for studying, one for programming, one for general use and one for media. I keep these on their respective workspaces to keep things organised.

# FAQ
## How do I use this?
Place the script into ~/.config/hypr/ and make it executable.
Create key bindings to this script in hyprland's config file.
Below is my default setup.
Add this to ~/.config/hypr/hyprland.conf
```
# Dynamic workspace manager variable setup
$app_launcher = rofi -show drun -show-icons -theme /home/s/.config/hypr/hyprland-dynamic-workspaces-manager/rofi-themes-collection/themes/rounded-nord-dark.rasi

$app_launcher_all = rofi -show combi -combi-modes run,drun -show-icons -theme /home/s/.config/hypr/hyprland-dynamic-workspaces-manager/rofi-themes-collection/themes/rounded-nord-dark.rasi

$window_switcher          = /home/s/.config/hypr/hyprland-dynamic-workspaces-manager/hyprland-dynamic-workspaces-manager.py --app-window-switcher
$workspace_switcher       = /home/s/.config/hypr/hyprland-dynamic-workspaces-manager/hyprland-dynamic-workspaces-manager.py --workspace
$move_window_to_workspace = /home/s/.config/hypr/hyprland-dynamic-workspaces-manager/hyprland-dynamic-workspaces-manager.py --move-window
$rename_workspace         = /home/s/.config/hypr/hyprland-dynamic-workspaces-manager/hyprland-dynamic-workspaces-manager.py --rename-workspace


# Keybindings
bind = $mainMod CTRL, space, exec, $app_launcher
bind = $mainMod CTRL SHIFT, space, exec, $app_launcher_all
bind = $mainMod ALT, space, exec, $window_switcher
bind = $mainMod, X, exec, $rename_workspace
bind = $mainMod, Z, exec, $workspace_switcher
bind = $mainMod SHIFT, Z, exec, $move_window_to_workspace

bind = $mainMod, tab, workspace, m-1
bind = $mainMod, F, fullscreen

# Move windows with mainMod + arrow keys
bind = $mainMod, left,  movefocus, l
bind = SUPER SHIFT, left,  movewindow, l
bind = SUPER SHIFT, right, movewindow, r
bind = SUPER SHIFT, up,    movewindow, u
bind = SUPER SHIFT, down,  movewindow, d 

# Other useful keybindings
bind = $mainMod, return, exec, $terminal
bind = $mainMod, Q, killactive,
```
- Switch to a workspace, WindowsKey+Z, then type one from the list.
- Create a /NEW/ workspace and switch to it, WindowsKey+Z, then type a new name. You can even use spaces in the workspace name :).
- Move a window to another workspace WindowsKey+Shift+Z, then type the workspace name.
- Move a window to a /NEW/ workspace WindowsKey+Shift+Z, then type the name of the new workspace.
- Rename a workspace WindowsKey+X
- App launcher WindowsKey+Ctrl+Space 
- App launcher including terminal commands WindowsKey+Ctrl+Shift+Space 
- Window Switcher  WindowsKey+Alt+Space 


## Can I still use the normal workspace hotkeys 1-9?
Yes. You can still use WindowsKey+1 to access the first workspace. You can rename this workspace and you can still switch to it using the normal workspace keybinding.

## How do I delete a workspace?
You don't! Once a workspace is empty, Hyprland will delete it after you switch to another workspace. This really does help with keeping our workspaces neat and condensed.


# Usage
```
usage: hyprland-dynamic-workspaces-manager.py [-h] [--app-window-switcher] [--workspace-switcher] [--move-window] [--rename-workspace]

options:
  -h, --help            show this help message and exit
  --app-window-switcher, --window-switcher, --app-switcher
                        Switch focus to another window.
  --workspace-switcher  Switch to another workspace.
  --move-window         Move the focused window to another workspace.
  --rename-workspace    Rename the current workspace.
```

# Credit
Thanks to Newmanls for the collection of rofi themes that I ship with this.
https://github.com/newmanls/rofi-themes-collection
