#!/usr/bin/env python3
import subprocess
import re
import argparse
import sys, os

auto_select = False # Set to True for auto selecting the first result in rofi's list that matches what we type. This saves you from pressing enter.

script_path = os.path.dirname( sys.argv[0] )
full_script_path = os.path.abspath( script_path )

rofi_theme_path = full_script_path + '/rofi-themes-collection/themes/rounded-nord-dark.rasi'
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
	all_workspaces = get_all_workspaces()
	current_workspace : Workspace = get_current_workspace()
	workspaces = ""
	current_workspace_index = -1

	for i in range(0, len(all_workspaces)):
		workspaces += all_workspaces[i].name + "\n"

		# Get the index number for our current workspace
		# We pass this to rofi to select/highlight the line our current workspace shows on.
		if current_workspace.id == all_workspaces[i].id:
			current_workspace_index = i
	

	if auto_select:
		str_auto_select = " -auto-select "
	else:
		str_auto_select = ""

	try:
		rofi_command = "printf \"" + workspaces + "\" | rofi -no-plugins -matching prefix " + str_auto_select + " " + rofi_theme + " -dmenu -i -p \"" + prompt_message + "\" -selected-row " + str( current_workspace_index )

		user_choice = subprocess.check_output( rofi_command, shell=True )
		user_choice = user_choice.decode().strip()
	except subprocess.CalledProcessError as some_error:
		# User probably pressed Esc to quit rofi, returning an exit code of 1.
		user_choice = ""

	return user_choice



def app_switcher():
	# Messy one-liner from emi89ro's post
	# https://www.reddit.com/r/hyprland/comments/15sro60/windowapp_switcher_recommendations/

	# Wofi one liner
	#subprocess.check_output("""bash -c "hyprctl dispatch focuswindow address:\"$(hyprctl -j clients | jq 'map(\"\\(.workspace.id) ∴ \\(.workspace.name) ┇ \\(.title) ┇ \\(.address)\")' | sed \"s/,$//; s/^\\[//; s/^\\]//; s/^[[:blank:]]*//; s/^\\"//; s/\\"$//\" | grep -v "^$" | wofi --insensitive -dO alphabetical | grep -o "0x.*$")\"" """, shell=True )

	rofi_command = "rofi -no-plugins " + rofi_theme + " -dmenu -i -p \"Switch to window\""
	subprocess.check_output("""bash -c "hyprctl dispatch focuswindow address:\"$(hyprctl -j clients | jq 'map(\"\\(.workspace.id) ∴ \\(.workspace.name) ┇ \\(.title) ┇ \\(.address)\")' | sed \"s/,$//; s/^\\[//; s/^\\]//; s/^[[:blank:]]*//; s/^\\"//; s/\\"$//\" | grep -v "^$" | """ + rofi_command + """ | grep -o "0x.*$")\"" """, shell=True )

def workspace_switcher():
	workspace = ask_user_which_workspace( "Switch to workspace:" )
	if workspace != "":
		subprocess.check_output( "hyprctl dispatch workspace name:"+workspace, shell=True )

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
