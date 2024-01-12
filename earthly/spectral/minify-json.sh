#!/usr/bin/env bash

# Minify all JSON in the directory if the file type is json
# Check if FILE_TYPE and DIR are not empty
if [ -n "${file_type}" ] && [ -n "${dir}" ]; then
    # Minify all JSON in the directory if the file type is json
    if [ "${file_type}" == "json" ]; then 
        # Loop through each JSON file in the directory
        for json_file in "${dir}"/*.json; do 
            # Check if the file is a regular file
            if [ -f "${json_file}" ]; then 
                # Minify the JSON file using jq and overwrite the original file
                jq -c . "${json_file}" > "${json_file}.tmp" && mv "${json_file}.tmp" "${json_file}" 
                echo "Compacted: ${json_file}" 
            fi 
        done 
    else 
        echo "File type is not JSON." 
    fi 
else 
    echo "FILE_TYPE or DIR is empty."
fi
