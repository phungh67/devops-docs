#!/usr/bin/env bash

INPUT_FILE=$1

# Validate inputs
if [[ -z "$1" ]]; then
  echo -e "\e[31mError: Missing required arguments.\e[0m"
  echo "Usage: $0 <path_to_configuration_file>"
  echo "Example: $0 hpp_sweep.txt"
  exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo -e "\e[31mError: Missing input configuration file '$INPUT_FILE'...\e[0m"
  exit 1
fi

# Define core paths
BASE_FILE="base4.cfg" 
# HOME_DIR="configs" 
TASK_DIR="HPP-Tuning" 

echo -e "\e[36m[INFO] Starting HPP parameter sweep from $INPUT_FILE...\e[0m"

while IFS= read -r line || [[ -n "$line" ]]; do
  
  # Skip empty lines and comments
  [[ -z "$line" || "$line" =~ ^# ]] && continue

  # Parse the columns
  read -r DIR_NAME IN_ORDER DISPATCH COMMIT ROB RS LSQ L2_SIZE L2_ASSOC <<< "$line"

  if [[ -z "$DIR_NAME" || -z "$LSQ" ]]; then
    echo -e "\e[33m[WARN] Skipping invalid line format: $line\e[0m"
    continue
  fi

  # Step 1: Create the correct directory for this specific test
  OUT_DIR="$TASK_DIR/$DIR_NAME"
  echo "--------------------------------------------------"
  echo -e "\e[34m[INFO] Processing: $DIR_NAME\e[0m"
  mkdir -p "$OUT_DIR"

  # Step 2: Copy the base4.cfg into the target directory
  TARGET_CFG="$OUT_DIR/$BASE_FILE"
  cp "$BASE_FILE" "$TARGET_CFG"
  echo "[INFO] Copied base configuration to $TARGET_CFG"

  # Step 3: Modify the configuration file in place
  sed -i.bak -E "s/^in_order[ \t]*=[ \t]*.*/in_order = $IN_ORDER/" "$TARGET_CFG"
  sed -i.bak -E "s/^dispatch_width[ \t]*=[ \t]*.*/dispatch_width = $DISPATCH/" "$TARGET_CFG"
  sed -i.bak -E "s/^commit_width[ \t]*=[ \t]*.*/commit_width = $COMMIT/" "$TARGET_CFG"
  sed -i.bak -E "s/^window_size[ \t]*=[ \t]*.*/window_size = $ROB/" "$TARGET_CFG"
  sed -i.bak -E "s/^rs_entries[ \t]*=[ \t]*.*/rs_entries = $RS/" "$TARGET_CFG"
  sed -i.bak -E "s/^outstanding_loads[ \t]*=[ \t]*.*/outstanding_loads = $LSQ/" "$TARGET_CFG"
  sed -i.bak -E "s/^outstanding_stores[ \t]*=[ \t]*.*/outstanding_stores = $LSQ/" "$TARGET_CFG"
  
  # NEW: Only modify L2 parameters if they were provided in the sweep text file
  if [[ -n "$L2_SIZE" ]]; then
    sed -i.bak -E '/^\[perf_model\/l2_cache\]/,/^\[/ s/^cache_size[ \t]*=[ \t]*.*/cache_size = '"$L2_SIZE"'/' "$TARGET_CFG"
  fi
  
  if [[ -n "$L2_ASSOC" ]]; then
    sed -i.bak -E '/^\[perf_model\/l2_cache\]/,/^\[/ s/^associativity[ \t]*=[ \t]*.*/associativity = '"$L2_ASSOC"'/' "$TARGET_CFG"
  fi
  
  rm -f "$OUT_DIR/*.bak"
  echo "[INFO] Modifications applied successfully."
  
  # Step 4: Run the test
  echo "[INFO] Starting simulation..."
  # (Adjust 'runsim_sim' or your specific runner command as needed)
  ./runsim.sh "$TASK_DIR/$DIR_NAME" "base4"

  # Step 5: Parse the results
  echo "[INFO] Parsing simulation runtime and power stats..."
  ./parser_jq.sh "$OUT_DIR" > "$OUT_DIR/sim_out.json"

  echo -e "\e[32m[SUCCESS] Finished $DIR_NAME\e[0m"

done < "$INPUT_FILE"

echo "--------------------------------------------------"
echo -e "\e[32m[SUCCESS] Batch automation complete!\e[0m"