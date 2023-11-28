#!/usr/bin/env bash
# Takes a single argument, the directory to check.

# Get our includes relative to this file's location.
source "$(dirname "$0")/include/colors.sh"

rc=0

# Create an associative array to store the file contents and their corresponding filenames
declare -A files

# Loop through all files with the .sh extension recursively
# Loop through all files with the .sh extension recursively, excluding symlinked directories
while IFS= read -r -d '' file; do
    # Calculate the MD5 hash of the file's contents
    hash=$(md5sum "${file}" | awk '{print $1}') || true

    # Check if the hash already exists in the array
    if [[ -n "${files[${hash}]}" ]]; then
        echo -e "${CYAN}Duplicated Bash Script: ${CYAN}${files[${hash}]} : ${RED}${file}${NC}"
        rc=1
    else
        # Add the hash and filename to the array
        files[${hash}]=${file}
        # Print the original file and the duplicate file
        echo -e "${CYAN}New Bash Script: ${CYAN}${file}${NC}"
    fi
done < <(find -P "$1" -type f -name "*.sh" -print0) || true

exit "${rc}"
