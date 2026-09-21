#!/usr/bin/env bash

INPUT_FILE=$1

# validate
if [[ -z "$1" ]]; then
  echo "Error: Missing required arguments."
  echo "Usage: $0 <path_to_configuration_file>"
  echo "Example: $0 configs_to_test.txt"
  exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Error: Missing input configuration file..."
  exit 1
fi

BASE_FILE="base1.txt" # the base, provided by TAs
HOME_DIR="configs" # the base for runsim_sim script
TASK_DIR="Lab1-Task2" # the base directory, aligns with task

echo "[INFO] Starting batch operation with cache-memory optimization from $INPUT_FILE..."

# read lines
while IFS= read -r line || [[ -n "$line" ]]; do
  
  [[ -z "$line" || "$line" =~ ^# ]] && continue

  read -r IL1_CONFIG IL1_LAT <<< "$line"

  if [[ -z "$IL1_CONFIG" || -z "$IL1_LAT" ]]; then
    echo "[WARN] Skipping invalid line format: $line"
    continue
  fi

  CONFIG_DIR_NAME=$(echo "$IL1_CONFIG" | tr ':' '-')
  OUT_DIR="$HOME_DIR/$TASK_DIR/$CONFIG_DIR_NAME"

  echo "--------------------------------------------------"
  echo "[INFO] Processing: $CONFIG_DIR_NAME (Latency: $IL1_LAT)"
  mkdir -p "$OUT_DIR"

  NEW_CONFIG_FILE="$OUT_DIR/configure.txt"
  cp "$BASE_FILE" "$NEW_CONFIG_FILE"

  sed -i.bak -E "s/^-cache:il1[ \t]+.*/-cache:il1 $IL1_CONFIG/" "$NEW_CONFIG_FILE"
  sed -i.bak -E "s/^-cache:il1lat[ \t]+.*/-cache:il1lat $IL1_LAT/" "$NEW_CONFIG_FILE"
  rm -f "$OUT_DIR/configure.txt.bak" 

  echo "[INFO] Created configuration template at $NEW_CONFIG_FILE"

  echo "[INFO] Starting SimpleScalar simulation..."
  ./runsim_sim "$TASK_DIR/$CONFIG_DIR_NAME" "configure"

  echo "[INFO] Parsing configuration static variables..."
  ./utils/variable-parser.sh "$NEW_CONFIG_FILE" > "$OUT_DIR/variable_base.json"

  echo "[INFO] Parsing simulation runtime stats..."
  ./utils/stats_parser_jq.sh "$OUT_DIR" > "$OUT_DIR/sim_out.json"

  echo "[INFO] Generating final metric report..."
  ./utils/calculate_result.sh "$OUT_DIR/sim_out.json" "$OUT_DIR/variable_base.json" > "$OUT_DIR/final_report.json"

  echo "[SUCCESS] Finished $CONFIG_DIR_NAME"

done < "$INPUT_FILE"

echo "--------------------------------------------------"
echo "[SUCCESS] Batch automation complete! All results stored in $TASK_DIR"