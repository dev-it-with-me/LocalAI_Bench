#!/bin/bash

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path-to-file-or-dir>"
    exit 1
fi

INPUT_PATH="$1"
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/svelte-check.log"

# Ensure the logs directory exists after changing to the 'ui' directory
mkdir -p "$LOG_DIR"

if [ -d "$INPUT_PATH" ]; then
    # If input is a directory, find all .svelte files and run svelte-check
    find "$INPUT_PATH" -type f -name "*.svelte" -print0 | xargs -0 npx svelte-check > "$LOG_FILE" 2>&1
elif [ -f "$INPUT_PATH" ]; then
    # If input is a file, run svelte-check on the file
    npx svelte-check "$INPUT_PATH" > "$LOG_FILE" 2>&1
else
    echo "Error: $INPUT_PATH is not a valid file or directory"
    exit 1
fi

# Example usage:
# To run svelte-check on a directory:
#   ./svelte-checks.sh /path/to/your/svelte/project
#
# To run svelte-check on a single file:
#   ./svelte-checks.sh /path/to/your/component.svelte