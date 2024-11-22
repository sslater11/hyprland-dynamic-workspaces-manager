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
import json

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
		rofi_command = "rofi -no-plugins -theme \'" + rofi_theme_path + "\' -dmenu -p \"Rename workspace to\""

		user_choice = subprocess.check_output( rofi_command, shell=True )
		user_choice = user_choice.decode().strip()
		
		current_workspace : Workspace = get_current_workspace()

		if user_choice != "":
			subprocess.check_output( "hyprctl dispatch renameworkspace " + current_workspace.id + " \"" + user_choice + "\"", shell=True )

	except subprocess.CalledProcessError as some_error:
		# User probably pressed Esc to quit rofi, returning an exit code of 1.
		user_choice = ""

def ask_user_which_workspace( prompt_message : str ):
	global is_auto_select
	all_workspaces = get_all_workspaces()
	all_workspaces_as_list_of_formatted_str = []
	current_workspace : Workspace = get_current_workspace()
	current_workspace_index = -1

	# Create a list of workspaces.
	for i in range(0, len(all_workspaces)):
		new_workspace_as_str = all_workspaces[i].name
		# Make escape sequences visible, i.e. '\n' becomes '\\n' so the user will see \n on their screen.
		# repr also keeps unicode so we can see emojis and other unicode symbols.
		new_workspace_as_str = repr(new_workspace_as_str)[1:-1] # [1:-1] - repr returns a string with quotes, so remove these first and last characters.
		# We want both "\n" and "\\\n" to display as "\\\n" to the user, so they see '\' and 'n' on their screen.
		# repr also turned a single backslash into two, so this line fixes this.
		new_workspace_as_str = new_workspace_as_str.replace( '\\\\','\\' )
		all_workspaces_as_list_of_formatted_str.append( new_workspace_as_str )

		# Get the index number for our current workspace
		# We pass this to rofi to select/highlight the line our current workspace shows on.
		if current_workspace.id == all_workspaces[i].id:
			current_workspace_index = i

	if is_auto_select:
		str_auto_select = "-auto-select"
	else:
		str_auto_select = ""

	try:
		rofi_command = ["rofi", "-no-plugins", str_auto_select, "-theme", rofi_theme_path, "-matching prefix", "-dmenu", "-i", "-p", prompt_message,     "-selected-row", str( current_workspace_index ) + " -a ", str( current_workspace_index )]

		all_workspaces_as_str = "\n".join(all_workspaces_as_list_of_formatted_str)
		with subprocess.Popen(rofi_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as rofi_process:
			# Directly write data to the stdin of rofi
			user_choice, errors = rofi_process.communicate( input=all_workspaces_as_str )

		# Rofi puts a newline on the end of our choice, so remove that.
		user_choice = user_choice.rstrip("\n")
		if user_choice in all_workspaces_as_list_of_formatted_str:
			# Set the user's choice as the original workspace name's string.
			workspace_index = all_workspaces_as_list_of_formatted_str.index( user_choice )
			user_choice = all_workspaces[ workspace_index ].name

        # TODO:
        # THERE'S A BUG HERE!
        # We can't have 2 workspaces with the same name, because we can only switch to one of them.
        # Currently there's no way in hyprctl to switch to a workspace with a negative id number.
        # All our named workspaces have negative numbers.
        # We're stuck with using workspace names as the identifier to switch workspaces.

	except subprocess.CalledProcessError as some_error:
		# User probably pressed Esc to quit rofi, returning an exit code of 1.
		user_choice = ""

	return user_choice


def get_active_window_address():
	active_window = subprocess.check_output("hyprctl -j activewindow", shell=True )
	active_window = active_window.decode().strip()

	window_address_pattern = "\"address\": \"(.*)\","
	regex_groups = re.search( window_address_pattern, active_window )

	if regex_groups != None:
		return regex_groups[1]
	else:
		print( "ERROR: No window address found, so returning an empty string and hoping the script doesn't break." )
		return ""

def window_switcher():
	global is_auto_select
	# Messy one-liner from emi89ro's post
	# https://www.reddit.com/r/hyprland/comments/15sro60/windowapp_switcher_recommendations/
	# Wofi one liner
	#subprocess.check_output("""bash -c "hyprctl dispatch focuswindow address:\"$(hyprctl -j clients | jq 'map(\"\\(.workspace.id) ∴ \\(.workspace.name) ┇ \\(.title) ┇ \\(.address)\")' | sed \"s/,$//; s/^\\[//; s/^\\]//; s/^[[:blank:]]*//; s/^\\"//; s/\\"$//\" | grep -v "^$" | wofi --insensitive -dO alphabetical | grep -o "0x.*$")\"" """, shell=True )

	active_window_address = get_active_window_address()
	active_window_index = 0
	separator = "__rofi_script_separator__"

	json_result = subprocess.check_output("hyprctl -j clients", shell=True )
	json_result = json_result.decode('utf-8').strip()
	all_windows = json.loads( json_result )
	
	# Create a list of all windows for passing to rofi.
	all_windows_as_str = ""
	for window in all_windows:
		if all_windows_as_str != "":
			all_windows_as_str += "\n"
		new_window_as_str = window["title"] + separator + window["workspace"]["name"]
		# Make escape sequences visible, i.e. '\n' becomes '\\n' so the user will see \n on their screen.
		# repr also keeps unicode so we can see emojis and other unicode symbols.
		new_window_as_str = repr(new_window_as_str)[1:-1] # [1:-1] - repr returns a string with quotes, so remove these first and last characters.
		# We want both "\n" and "\\\n" to display as "\\\n" to the user, so they see '\' and 'n' on their screen.
		# repr also turned a single backslash into two, so this line fixes this.
		new_window_as_str = new_window_as_str.replace( '\\\\','\\' )
		all_windows_as_str += new_window_as_str

	# Loop through all windows, check if the current window id is equal to the current one.
	# Save that index and use it to highlight the row in rofi.
	active_window_address = get_active_window_address()
	active_window_index = 0
	index_counter = -1
	for window in all_windows:
		index_counter += 1
		if window["address"] == active_window_address:
			# Set the index number of our active window in this list.
			active_window_index = index_counter
			break

	if is_auto_select:
		str_auto_select = "-auto-select"
	else:
		str_auto_select = ""

	user_choice = ""
	try:
		# rofi's dmenu option: -format 'i' -- returns the index of the selected entry.
		rofi_command = ["rofi", "-no-plugins", str_auto_select, "-theme", rofi_theme_path, "-dmenu", "-no-custom", "-format", "i", "-i", "-p", "Switch to window", "-selected-row", str(active_window_index), "-a", str(active_window_index), "-display-columns", "1,2", "-display-column-separator", separator ]

		with subprocess.Popen(rofi_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as rofi_process:
			# Directly write data to the stdin of rofi
			input_data = all_windows_as_str
			user_choice, errors = rofi_process.communicate( input=input_data )

		if user_choice != "":
			selected_index = int( user_choice.strip() )
			user_choice = all_windows[ selected_index ][ "address" ]
	except subprocess.CalledProcessError as some_error:
		# User probably pressed Esc to quit rofi, returning an exit code of 1.
		user_choice = ""

	if user_choice != "":
		print( subprocess.check_output( "hyprctl dispatch focuswindow address:" + user_choice, shell=True ) )

def workspace_switcher():
	workspace = ask_user_which_workspace( "Switch to workspace:" )
	if workspace != "":
		# Default hyprland workspace switching. Rubbish for our use case of accessing any workspace at any time on any monitor.
		#subprocess.check_output( "hyprctl dispatch workspace name:\"" + workspace + "\"", shell=True )

		# XMonad style workspace switching. It will swap 2 workspaces, bringing the new one to the current monitor we're on. If both workspaces are on monitors, you will see them swap places.
		subprocess.check_output( "hyprctl dispatch focusworkspaceoncurrentmonitor name:\"" + workspace + "\"", shell=True )

def move_window_to_workspace():
	workspace = ask_user_which_workspace( "Move window to workspace" )
	if workspace != "":
		subprocess.check_output( "hyprctl dispatch movetoworkspace name:\"" + workspace + "\"", shell=True )


if __name__ == "__main__":
	rofi_themes = [
		"nord",
		"rounded-blue-dark",
		"rounded-gray-dark",
		"rounded-green-dark",
		"rounded-nord-dark",
		"rounded-orange-dark",
		"rounded-pink-dark",
		"rounded-purple-dark",
		"rounded-red-dark",
		"rounded-yellow-dark",
		"simple-tokyonight",
		"spotlight-dark",
		"spotlight",
		"squared-everforest",
		"squared-material-red",
		"squared-nord"
	]

	# Initialize parser
	parser = argparse.ArgumentParser()

	parser.add_argument("--window-switcher",    action = "store_true",                        help = "Switch focus to another window.")
	parser.add_argument("--workspace-switcher", action = "store_true",                        help = "Switch to another workspace.")
	parser.add_argument("--move-window",        action = "store_true",                        help = "Move the focused window to another workspace.")
	parser.add_argument("--rename-workspace",   action = "store_true",                        help = "Rename the current workspace.")
	parser.add_argument("--auto-select",        action = "store_true",                        help = "Will automatically select an entry in the list as you type (default: False)")
	parser.add_argument("--no-auto-select",     action = "store_false", dest = "auto-select", help = "Will NOT automatically select an entry in the list as you type (default: True)")

	parser.add_argument(
		'--theme',
		choices=rofi_themes,
		default="rounded-orange-dark",
		help='Set the theme'
	)

	parser.add_argument(
		'--theme-file',
		type=str,
		help='Select a custom theme file for rofi. E.g. --theme-file "~/path/to/your/theme.rasi"'
	)

	parser.set_defaults(auto_select=False)

	# Read arguments from command line
	args = parser.parse_args()

	# theme path
	script_path = os.path.dirname( sys.argv[0] )
	full_script_path = os.path.abspath( script_path )
	rofi_theme_path = full_script_path + '/rofi-themes-collection/themes/' + args.theme + ".rasi"

	is_auto_select = args.auto_select # Set to True for auto selecting the first result in rofi's list that matches what we type. This saves you from pressing enter.

	# Override the theme with user's custom theme.
	if args.theme_file:
		rofi_theme_path = args.theme_file

	if args.window_switcher:
		window_switcher()
	elif args.workspace_switcher:
		workspace_switcher()
	elif args.move_window:
		move_window_to_workspace()
	elif args.rename_workspace:
		rename_workspace()
	else:
		parser.print_help()
