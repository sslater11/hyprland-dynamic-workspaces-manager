#!/bin/bash
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
