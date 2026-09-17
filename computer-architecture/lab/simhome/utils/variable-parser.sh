#!/usr/bin/env bash

TARGET_FILE=$1
HOME_DIR="."

echo "[DEBUG] Value of target file: $1"

if [[ ! -f "$TARGET_FILE" ]]; then
  echo "Error: File '$TARGET_FILE' not found." >&2
  exit 1
fi

awk '
  # Match lines that begin with optional spaces followed by a dash
  /^[ \t]*-/ {
    var = $1
    # Strip the variable name and leading whitespace to capture the full value
    sub(/^[ \t]*-[^ \t]+[ \t]*/, "")
    printf "%-20s : %s\n", var, $0
  }
' "$TARGET_FILE"