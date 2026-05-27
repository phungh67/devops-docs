#!/bin/bash

# Define the model being tested
MODEL="gemma4"

# Define the exact suite of probes to run
PROBES=(
    "promptinject"
    "encoding"
    "dan.Dan_8_0"
    "dan.Dan_9_0"
    "dan.Dan_10_0"
    "dan.Dan_11_0"
)

echo "================================================="
echo " Starting Baseline Control Test (Bare Ollama) "
echo " Target Model: $MODEL"
echo "================================================="

for probe in "${PROBES[@]}"
do
   echo -e "\n---> Running Probe: $probe"
   python3 -m garak --model_type ollama --model_name "$MODEL" --probes "$probe" --generations 1
   echo "---> Finished $probe"
done

echo -e "\n[✔] Baseline testing complete. Check the generated .report.html files."