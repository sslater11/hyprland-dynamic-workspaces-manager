#!/bin/bash
echo "+-------------------+"
echo "|--Theme Previewer--|"
echo "+-------------------+"
echo ""
echo "Warning, this will spam you out with multiple rofi launchers!"
echo "You should press ESC multiple times to quit out of these."
echo ""
echo "Do you want to continue?"
read -p "Are you sure? (y/n): " yn
case $yn in
  [Yy]* ) echo "Proceeding...";;
  [Nn]* ) echo "Aborting..."; exit;;
  * ) echo "Invalid input. Please answer y or n. Exiting..."; exit;;
esac


declare -a all_themes=("nord" "rounded-blue-dark" "rounded-gray-dark" "rounded-green-dark" "rounded-nord-dark" "rounded-orange-dark" "rounded-pink-dark" "rounded-purple-dark" "rounded-red-dark" "rounded-yellow-dark" "simple-tokyonight" "spotlight-dark" "spotlight" "squared-everforest" "squared-material-red" "squared-nord")

for theme in "${all_themes[@]}"; do
	echo "Showing theme: $theme"
	SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
	$SCRIPT_DIR/hyprland-dynamic-workspaces-manager.py --window-switcher --theme "$theme" > /dev/null 2>&1
done
