#!/usr/bin/env bash

# Assign arguments to variables, applying a default value for the third argument
SIM_FILE=$1
CFG_FILE=$2
OUT_FILE=${3:-"output_default_calculated.json"}

# 1. Validation checks
if [[ -z "$SIM_FILE" || -z "$CFG_FILE" ]]; then
  echo "Error: Missing required arguments."
  echo "Usage: $0 <simulation_result.json> <static_configuration.json> [output.json]"
  exit 1
fi

if [[ ! -f "$SIM_FILE" ]]; then
  echo "Error: Simulation result file '$SIM_FILE' not found."
  exit 1
fi

if [[ ! -f "$CFG_FILE" ]]; then
  echo "Error: Static configuration file '$CFG_FILE' not found."
  exit 1
fi

# 2. Debug outputs to verify which values are taken
echo "[DEBUG] Simulation result file : $SIM_FILE"
echo "[DEBUG] Static config file     : $CFG_FILE"
echo "[DEBUG] Output target file     : $OUT_FILE"

# Extract the Miss Penalty (MP) from the static configuration file using jq
# This specifically parses the value associated with "-mem:lat" to verify it before processing
MP_VALUE=$(jq -r '."-mem:lat".value | split(" ")[0]' "$CFG_FILE")
echo "[DEBUG] Extracted Miss Penalty (MP) from $CFG_FILE: $MP_VALUE cycles"

# 3. Calculate metrics and output to JSON
jq -s '
  # Re-extract the Miss Penalty inside the main jq script
  (.[1]["-mem:lat"].value | split(" ")[0] | tonumber) as $mp |

  # Iterate through each benchmark in the simulation result file
  .[0] | map_values(
    
    # Calculate CPI_0
    (.sim_CPI - (.mpi_il1 * $mp) - (.mpi_dl1 * $mp)) as $cpi_0 |
    
    {
      "Instruction Count": .sim_num_insn,
      "Execution Time in cycles": .sim_cycle,
      "CPI_base": .sim_CPI,
      "MPI I-L1": .mpi_il1,
      "MPI D-L1": .mpi_dl1,
      "CPI_0": $cpi_0,
      "SP_ideal": (.sim_CPI / $cpi_0),
      "Memory Stall %": (((.sim_CPI - $cpi_0) / .sim_CPI) * 100)
    }
  )
' "$SIM_FILE" "$CFG_FILE" > "$OUT_FILE"

echo "[SUCCESS] Computed metrics saved to $OUT_FILE"