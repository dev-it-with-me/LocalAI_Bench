#!/bin/bash

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path-to-file-or-dir>"
    exit 1
fi

INPUT_PATH="$1"
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/mypy-log.log"

mkdir -p "$LOG_DIR"

if [ -d "$INPUT_PATH" ]; then
    # If input is a directory, find all .py files and run mypy
    find "$INPUT_PATH" -type f -name "*.py" -print0 | xargs -0 mypy --explicit-package-bases --check-untyped-defs > "$LOG_FILE" 2>&1
elif [ -f "$INPUT_PATH" ]; then
    # If input is a file, run mypy on the file
    mypy --explicit-package-bases --check-untyped-defs "$INPUT_PATH" > "$LOG_FILE" 2>&1
else
    echo "Error: $INPUT_PATH is not a valid file or directory"
    exit 1
fi

# Example usage:
# To run mypy on a directory:
#   ./mypy-checks.sh /path/to/your/python/project
#
# To run mypy on a single file:
#   ./mypy-checks.sh /path/to/your/file.py