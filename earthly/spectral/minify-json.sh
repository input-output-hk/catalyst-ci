#!/usr/bin/env bash

# Minify all JSON in the directory if the file type is json
if [[ "${FILE_TYPE}" == "json" ]]; then 
    # Loop through each JSON file in the directory
    for json_file in "${DIR}"/*.json; do 
        # Check if the file is a regular file
        if [[ -f "${json_file}" ]]; then 
            # Minify the JSON file using jq and overwrite the original file
            jq -c . "${json_file}" > "${json_file}.tmp" && mv "${json_file}.tmp" "${json_file}" 
            echo "Compacted: ${json_file}" 
        fi 
    done 
else 
    echo "File type is not JSON." 
fi 
