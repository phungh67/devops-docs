#!/usr/bin/env bash

TARGET_FILE=$1
OUTPUT_DIR=$2

echo "[DEBUG] Value of target file: $TARGET_FILE" >&2

if [ -z $OUTPUT_DIR ]; then
    echo "[WARN] Value of output file is not set, fall back to default file name: variable_${TARGET_FILE}.json"
    OUTPUT_DIR="variable_base"
fi

if [[ ! -f "$TARGET_FILE" ]]; then
  echo "Error: File '$TARGET_FILE' not found." >&2
  exit 1
fi

awk '
  BEGIN { desc = "" }
  
  # Clear the description buffer on empty lines
  /^$/ { desc = ""; next }
  
  # 1. Match commented parameters: starts with "#", optional spaces, then "-"
  /^#[ \t]*-/ {
    sub(/^#[ \t]*/, "")              # Strip the "#" and leading whitespace
    var = $1
    sub(/^[ \t]*-[^ \t]+[ \t]*/, "") # Strip the variable name to isolate the value
    val = $0
    sub(/[ \t]+$/, "", val)          # Trim trailing whitespace for clean JSON
    
    # Print as TSV with status "commented(unused)"
    printf "%s\t%s\t%s\tcommented(unused)\n", var, val, desc
    desc = ""
    next
  }
  
  # 2. Match description lines: starts with "#", but NOT followed by "-"
  /^#[ \t]*[^-]/ {
    sub(/^#[ \t]*/, "")
    if (desc != "") desc = desc " " $0
    else desc = $0
    next
  }
  
  # 3. Match active parameters: starts with optional spaces, then "-"
  /^[ \t]*-/ {
    var = $1
    sub(/^[ \t]*-[^ \t]+[ \t]*/, "")
    val = $0
    sub(/[ \t]+$/, "", val)          # Trim trailing whitespace
    
    # Print as TSV with status "active"
    printf "%s\t%s\t%s\tactive\n", var, val, desc
    desc = ""
    next
  }
' "$TARGET_FILE" | jq -R -s '
  # Transform the 4-column TSV into JSON
  [ 
    split("\n")[] | select(length > 0) | split("\t") | 
    { 
      (.[0]): { 
        "description": .[2], 
        "value": .[1],
        "status": .[3]
      } 
    } 
  ] | add
' >> ${OUTPUT_DIR}.json