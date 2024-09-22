#!/usr/bin/env python3

# Copyright (C) 2024 Simon Slater
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import subprocess
import re
import argparse
import sys, os

auto_select = False # Set to True for auto selecting the first result in rofi's list that matches what we type. This saves you from pressing enter.

script_path = os.path.dirname( sys.argv[0] )
full_script_path = os.path.abspath( script_path )

rofi_theme_path = full_script_path + '/rofi-themes-collection/themes/rounded-orange-dark.rasi'
#rofi_theme = "" # Leave this blank to use the default rofi theme.
# Example of a theme being used.
rofi_theme = " -theme \'" + rofi_theme_path + "\'"


class Workspace:
	def __init__( self, id : str, name : str ):
		self.id : str = id
		self.name : str = name

# Returns a list of Workspace objects for each workspace.
def get_all_workspaces():
	all_workspaces = []
	workspaces = subprocess.check_output( "hyprctl workspaces", shell=True )
	workspaces = workspaces.decode().strip()

	for line in workspaces.split("\n"):
		workspace_pattern = "(^workspace ID )(-*[0-9]+) \\((.*)(\\) on .*:$)"
		regex_groups = re.search( workspace_pattern, line )

		if regex_groups != None:
			all_workspaces.append( Workspace( id = regex_groups.group( 2 ), name = regex_groups.group( 3 ) ))

	
	return all_workspaces

def get_current_workspace():
	try:
		command = "hyprctl activeworkspace"
		workspace = subprocess.check_output( command, shell=True )
		workspace = workspace.decode().strip()
		for line in workspace.split("\n"):
			workspace_pattern = "(^workspace ID )(-*[0-9]+) \\((.*)(\\) on .*:$)"
			regex_groups = re.search( workspace_pattern, line )

			if regex_groups != None:
				return Workspace( id = regex_groups.group(2), name = regex_groups.group(2) )
	except subprocess.CalledProcessError as some_error:
		# User probably pressed Esc to quit rofi, returning an exit code of 1.
		return None
	return None

def rename_workspace():
	try:
		rofi_command = "rofi -no-plugins " + rofi_theme + " -dmenu -p \"Rename workspace to\""

		user_choice = subprocess.check_output( rofi_command, shell=True )
		user_choice = user_choice.decode().strip()
		
		current_workspace : Workspace = get_current_workspace()

		if user_choice != "":
			subprocess.check_output( "hyprctl dispatch renameworkspace " + current_workspace.id + " " + user_choice, shell=True )

	except subprocess.CalledProcessError as some_error:
		# User probably pressed Esc to quit rofi, returning an exit code of 1.
		user_choice = ""
	






def ask_user_which_workspace( prompt_message : str ):
	global auto_select
	separator = "__rofi_script_separator__"
	all_workspaces = get_all_workspaces()
	current_workspace : Workspace = get_current_workspace()
	workspaces = ""
	current_workspace_index = -1

	for i in range(0, len(all_workspaces)):
		workspaces += all_workspaces[i].name + separator + all_workspaces[i].id
		if i != len( all_workspaces ) - 1:
			workspaces += "\n"

		# Get the index number for our current workspace
		# We pass this to rofi to select/highlight the line our current workspace shows on.
		if current_workspace.id == all_workspaces[i].id:
			current_workspace_index = i
	

	if auto_select:
		str_auto_select = " -auto-select "
	else:
		str_auto_select = ""

	try:
		rofi_command = "echo -e \"" + workspaces + "\" | rofi -no-plugins -matching prefix " + str_auto_select + " " + rofi_theme + " -dmenu -i -p \"" + prompt_message + "\" -selected-row " + str( current_workspace_index ) + " -a " + str( current_workspace_index ) + " -display-columns 1 -display-column-separator \"" + separator + "\""

		user_choice = subprocess.check_output( rofi_command, shell=True )
		user_choice = user_choice.decode().strip()

        # TODO:
        # THERE'S A BUG HERE!
        # We can't have 2 workspaces with the same name, because we can only switch to one of them.
        # Currently there's no way in hyprctl to switch to a workspace with a negative id number.
        # All our named workspaces have negative numbers.
        # We're stuck with using workspace names as the identifier to switch workspaces.

		user_choice = user_choice.split( separator )[0]
	except subprocess.CalledProcessError as some_error:
		# User probably pressed Esc to quit rofi, returning an exit code of 1.
		user_choice = ""

	return user_choice


def get_active_window_address():
	active_window = subprocess.check_output("""bash -c "hyprctl -j activewindow" """, shell=True )
	active_window = active_window.decode().strip()

	window_address_pattern = "\"address\": \"(.*)\","
	regex_groups = re.search( window_address_pattern, active_window )

	if regex_groups != None:
		return regex_groups[1]
	else:
		print( "ERROR: No window address found, so returning an empty string and hoping the script doesn't break." )
		return ""

def app_switcher():
	# Messy one-liner from emi89ro's post
	# https://www.reddit.com/r/hyprland/comments/15sro60/windowapp_switcher_recommendations/
	# Wofi one liner
	#subprocess.check_output("""bash -c "hyprctl dispatch focuswindow address:\"$(hyprctl -j clients | jq 'map(\"\\(.workspace.id) ∴ \\(.workspace.name) ┇ \\(.title) ┇ \\(.address)\")' | sed \"s/,$//; s/^\\[//; s/^\\]//; s/^[[:blank:]]*//; s/^\\"//; s/\\"$//\" | grep -v "^$" | wofi --insensitive -dO alphabetical | grep -o "0x.*$")\"" """, shell=True )

	active_window_address = get_active_window_address()
	active_window_index = 0
	separator = "__rofi_script_separator__"

	# Get a list of all windows open
	jq = "jq 'map(\\\"\\(.title)" + separator + "\\(.workspace.name)" + separator + "\\(.address)\\\")' "
	jq = jq.replace("\\n", "\n")
	jq_result = subprocess.check_output("""bash -c "hyprctl -j clients | """ + jq + """    """ +"\"", shell=True )
	jq_result = jq_result.decode().strip()

	# Convert jquery of open windows to a list of strings.
	jq_result = jq_result.split("\n")
	# remove the starting and ending braces [ ]
	jq_result = jq_result[1:-1]

	all_windows = ""
	for i in range( len( jq_result ) ):
		# Remove whitespace, the quote at the start and end, and also the comma at the end.
		window = jq_result[i].strip().lstrip("\"").rstrip(",").rstrip("\"")
		all_windows += window
		if i != len( jq_result ) - 1:
			all_windows += "\\n"

		# Set the index number of our active window in this list.
		window_address = window.split( separator )[2]
		if window_address == active_window_address:
			active_window_index = i

	rofi_command = "echo -e \"" + all_windows + "\" | rofi -no-plugins " + rofi_theme + " -dmenu -i -p \"Switch to window\" -selected-row " + str(active_window_index) + " -a " + str(active_window_index) + " -display-columns 1,2 -display-column-separator \"" + separator + "\""
	user_choice = subprocess.check_output( rofi_command, shell=True )
	user_choice = user_choice.decode().strip()

	if user_choice != "":
		user_choice = user_choice.split( separator )
		window_address = user_choice[2]
		print( subprocess.check_output( "hyprctl dispatch focuswindow address:" + window_address, shell=True ) )
	print( "Warning: This doesn't handle backslash escape characters, like \\n. Need to update code to handle this. If a window has \\n in their title, it will show as 2 different windows in the list." )


def workspace_switcher():
	workspace = ask_user_which_workspace( "Switch to workspace:" )
	if workspace != "":
        # Default hyprland workspace switching. Rubbish for our use case of accessing any workspace at any time on any monitor.
		#subprocess.check_output( "hyprctl dispatch workspace name:"+workspace, shell=True )

        # XMonad style workspace switching. It will swap 2 workspaces, bringing the new one to the current monitor we're on. If both workspaces are on monitors, you will see them swap places.
		subprocess.check_output( "hyprctl dispatch focusworkspaceoncurrentmonitor name:"+workspace, shell=True )

def move_window_to_workspace():
	workspace = ask_user_which_workspace( "Move window to workspace" )
	if workspace != "":
		subprocess.check_output( "hyprctl dispatch movetoworkspace name:"+workspace, shell=True )
	



# Initialize parser
parser = argparse.ArgumentParser()

parser.add_argument("--app-window-switcher","--window-switcher","--app-switcher", help = "Switch focus to another window.", action ="store_true")
parser.add_argument("--workspace-switcher", help = "Switch to another workspace.", action ="store_true")
parser.add_argument("--move-window", help = "Move the focused window to another workspace.", action ="store_true")
parser.add_argument("--rename-workspace", help = "Rename the current workspace.", action ="store_true")

# Read arguments from command line
args = parser.parse_args()

if args.app_window_switcher:
	app_switcher()
elif args.workspace_switcher:
	workspace_switcher()
elif args.move_window:
	move_window_to_workspace()
elif args.rename_workspace:
	rename_workspace()
else:
	parser.print_help()


#write a function for moving the current window to another workspace.
#then add arguments for this script
