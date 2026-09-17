#!/usr/bin/env bash

# Check for required arguments
# $1 = Cache configuration string (e.g., il1:128:32:2:l) - formatted according to base1.txt
# $2 = Cache hit latency in cycles (e.g., 2) - derived from Table 2
if [[ -z "$1" || -z "$2" ]]; then
  echo "Error: Missing required arguments."
  echo "Usage: $0 <il1_config_string> <hit_latency>"
  echo "Example: $0 il1:64:32:2:l 1"
  exit 1
fi

IL1_CONFIG=$1
IL1_LAT=$2

# working directory
BASE_FILE="base1.txt"
TASK_DIR="Lab1-Task2"

# generate corresponding directory
CONFIG_DIR_NAME=$(echo "$IL1_CONFIG" | tr ':' '-')
OUT_DIR="$TASK_DIR/$CONFIG_DIR_NAME"

echo "[INFO] Initializing optimization run for: $CONFIG_DIR_NAME (Latency: $IL1_LAT)"
mkdir -p "$OUT_DIR"

# copy configuration
NEW_CONFIG_FILE="$OUT_DIR/configure.txt"
cp "$BASE_FILE" "$NEW_CONFIG_FILE"

# only changes corresponding cache
sed -i.bak -E "s/^-cache:il1[ \t]+.*/-cache:il1 $IL1_CONFIG/" "$NEW_CONFIG_FILE"
sed -i.bak -E "s/^-cache:il1lat[ \t]+.*/-cache:il1lat $IL1_LAT/" "$NEW_CONFIG_FILE"
rm -f "$OUT_DIR/configure.txt.bak" 

echo "[INFO] Created configuration template at $NEW_CONFIG_FILE"

# simulation
echo "[INFO] ./runsim_sim $DIR $CFG with DIR = configure dir while $CFG = name without extension"
./runsim_sim "$OUT_DIR" "configure"

# cfg parsing
echo "[INFO] Parsing configuration static variables..."
./util/variable-parser.sh "$NEW_CONFIG_FILE" > "$OUT_DIR/variable_base.json"

# output report
echo "[INFO] Parsing simulation runtime stats..."
./util/stats_parser_jq.sh "$OUT_DIR" > "$OUT_DIR/sim_out.json"

# calculate according to table in task 1
echo "[INFO] Generating final metric report..."
./util/calculate_result_2.sh "$OUT_DIR/sim_out.json" "$OUT_DIR/variable_base.json" "$OUT_DIR/final_report.json"

echo "[SUCCESS] Automation complete! View results at $OUT_DIR/final_report.json"