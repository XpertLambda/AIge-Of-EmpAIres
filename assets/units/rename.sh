#!/bin/bash

# Find all files named sprite_sheet.webp in the directory recursively
find . -type f -name "sprite_sheet.webp" | while read -r file; do
    # Extract components from the directory structure
    unit_name=$(echo "$file" | cut -d'/' -f2)          # Extract the unit name
    team_color=$(echo "$file" | cut -d'/' -f3)         # Extract the team color
    state=$(echo "$file" | cut -d'/' -f4)              # Extract the state

    # Define the new name
    new_name="${unit_name}-${team_color}-${state}_Sheet.webp"

    # Get the directory path for the file
    dir=$(dirname "$file")

    # Rename the file
    mv "$file" "$dir/$new_name"
done
