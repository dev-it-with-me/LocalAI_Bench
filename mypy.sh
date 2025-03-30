#!/bin/bash

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path-to-file>"
    exit 1
fi

FILE_PATH="$1"
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/mypy-log.log"

mkdir -p "$LOG_DIR"

mypy --explicit-package-bases --check-untyped-defs "$FILE_PATH" > "$LOG_FILE" 2>&1

