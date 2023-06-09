#!/bin/bash

# Define the path to your Python script
python_script_path="test.py"

new_files_list=()
modified_files_list=()

# Retrieve the newly added file names in the "data" folder
while IFS= read -r file; do
    new_files_list+=("$file")
done < <(git diff --cached --name-only --diff-filter=A "data/")

# Retrieve the modified file names in the "data" folder
while IFS= read -r file; do
    modified_files_list+=("$file")
done < <(git diff --cached --name-only --diff-filter=M "data/")

# Convert new_files_list to a comma-separated string
new_files_string=$(IFS=,; echo "${new_files_list[*]}")

# Check if new_files_list has a length greater than zero
if [[ ${#new_files_list[@]} -gt 0 ]]; then
    # Prompt user for input
    read -r -p "New files detected. Do you want to continue? [y/n]: " response
    if [[ $response =~ ^[Yy]$ ]]; then
        echo "sdds"
        # User confirmed, run the Python script
        #python "$python_script_path" "$new_files_string"
        exit 0
    else
        # User declined, exit without running the Python script
        echo "Pre-commit process aborted."
        exit 0
    fi
fi