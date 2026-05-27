#!/bin/bash

# Define the target bridge function
TARGET="daemon_bridge#probe"

# Define the exact suite of probes to run (must match the baseline for accurate comparison)
PROBES=(
    "promptinject"
    "encoding"
    "dan.Dan_8_0"
    "dan.Dan_9_0"
    "dan.Dan_10_0"
    "dan.Dan_11_0"
)

echo "================================================="
echo " Starting Experimental Test (Shielded Daemon) "
echo " Target Endpoint: $TARGET"
echo "================================================="

for probe in "${PROBES[@]}"
do
   echo -e "\n---> Running Probe: $probe"
   python3 -m garak --target_type function --target_name "$TARGET" --probes "$probe" --generations 1
   echo "---> Finished $probe"
done

echo -e "\n[✔] Shielded testing complete. Compare these .report.html files with the baseline."