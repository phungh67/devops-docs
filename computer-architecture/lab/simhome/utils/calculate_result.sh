#!/usr/bin/env bash

# Assign arguments to variables (Removed the OUT_FILE argument)
SIM_FILE=$1
CFG_FILE=$2

# 1. Validation checks
if [[ -z "$SIM_FILE" || -z "$CFG_FILE" ]]; then
  echo "Error: Missing required arguments." >&2
  echo "Usage: $0 <simulation_result.json> <static_configuration.json>" >&2
  exit 1
fi

if [[ ! -f "$SIM_FILE" ]]; then
  echo "Error: Simulation result file '$SIM_FILE' not found." >&2
  exit 1
fi

if [[ ! -f "$CFG_FILE" ]]; then
  echo "Error: Static configuration file '$CFG_FILE' not found." >&2
  exit 1
fi

# 2. Debug outputs routed to stderr to protect stdout
echo "[DEBUG] Simulation result file : $SIM_FILE" >&2
echo "[DEBUG] Static config file     : $CFG_FILE" >&2

# Extract the Miss Penalty (MP) from the static configuration file using jq
MP_VALUE=$(jq -r '."-mem:lat".value | split(" ")[0]' "$CFG_FILE")
echo "[DEBUG] Extracted Miss Penalty (MP) from $CFG_FILE: $MP_VALUE cycles" >&2

# 3. Calculate metrics and output to JSON (prints directly to stdout)
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
' "$SIM_FILE" "$CFG_FILE"

echo "[SUCCESS] Computed metrics generated successfully" >&2