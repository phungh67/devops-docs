#!/bin/bash

if [ "$#" -lt 1 ]; then
    echo -e "\e[31mUsage: $0 <Simulation Directory>\e[0m" >&2
    exit 1
fi

Sim_DIR=$1
benchmarks=( qsort gsm jpeg )

echo -e "\e[36m[INFO] Starting JSON parsing for directory: $Sim_DIR\e[0m" >&2

for b in "${benchmarks[@]}"; do
    sim_out="$Sim_DIR/$b/sim.out"
    power_out="$Sim_DIR/$b/power.txt"
    
    # Locate the configuration file in the benchmark directory
    cfg_file=$(ls "$Sim_DIR/$b"/*.cfg 2>/dev/null | head -n 1)
    
    # ---------------------------------------------------------
    # Configuration Parsing
    # ---------------------------------------------------------
    if [ -f "$cfg_file" ]; then
        # Extract frequency and core_model, stripping out comments, spaces, and quotes
        freq_ghz=$(grep -m1 "frequency" "$cfg_file" | awk -F'=' '{print $2}' | awk '{print $1}')
        core_model=$(grep -m1 "core_model" "$cfg_file" | awk -F'=' '{print $2}' | tr -d ' "')
    else
        freq_ghz=1.0
        core_model="unknown"
    fi
    
    # Calculate clock period in nanoseconds (1 / GHz)
    clock_period=$(awk "BEGIN {printf \"%.5f\", 1.0 / $freq_ghz}")

    # ---------------------------------------------------------
    # Performance Parsing & Skipping Logic
    # ---------------------------------------------------------
    if [ ! -f "$sim_out" ]; then
        echo -e "\e[33m[WARN] $sim_out missing for $b. Skipping.\e[0m" >&2
        continue
    fi

    insn=$(grep -m1 "Instructions" "$sim_out" | awk '{print $3}')
    cycles=$(grep -m1 "Cycles" "$sim_out" | awk '{print $3}')
    
    insn=${insn:-0}
    cycles=${cycles:-0}

    if [ "$insn" -eq 0 ]; then
        echo -e "\e[33m[WARN] Instructions = 0 for $b. Skipping benchmark.\e[0m" >&2
        continue
    fi

    cpi=$(awk "BEGIN {printf \"%.5f\", $cycles / $insn}")
    time_ns=$(awk "BEGIN {printf \"%.5f\", $cycles * $clock_period}")

    # ---------------------------------------------------------
    # Power Parsing
    # ---------------------------------------------------------
    if [ ! -f "$power_out" ]; then
        echo -e "\e[33m[WARN] $power_out missing for $b. Defaulting power to 0.\e[0m" >&2
        area=0; peak_dyn=0; runtime_dyn=0; leakage=0;
    else
        core_stats=$(grep -A6 "Core:" "$power_out")
        
        area=$(echo "$core_stats" | grep -m1 "Area =" | awk '{print $(NF-1)}')
        peak_dyn=$(echo "$core_stats" | grep -m1 "Peak Dynamic =" | awk '{print $(NF-1)}')
        runtime_dyn=$(echo "$core_stats" | grep -m1 "Runtime Dynamic =" | awk '{print $(NF-1)}')
        leakage=$(echo "$core_stats" | grep -m1 "Subthreshold Leakage =" | awk '{print $(NF-1)}')
        
        area=${area:-0}; peak_dyn=${peak_dyn:-0}; runtime_dyn=${runtime_dyn:-0}; leakage=${leakage:-0}
    fi

    # ---------------------------------------------------------
    # JSON Emission
    # ---------------------------------------------------------
    jq -n \
        --arg test "$b" \
        --arg model "$core_model" \
        --arg freq "$freq_ghz" \
        --arg insn "$insn" \
        --arg cyc "$cycles" \
        --arg cpi "$cpi" \
        --arg time "$time_ns" \
        --arg area "$area" \
        --arg peak "$peak_dyn" \
        --arg runtime "$runtime_dyn" \
        --arg leak "$leakage" \
        '{
            ($test): {
                "Core_Model": $model,
                "Frequency_GHz": ($freq | tonumber),
                "Instructions": ($insn | tonumber),
                "Cycles": ($cyc | tonumber),
                "CPI": ($cpi | tonumber),
                "Time_ns": ($time | tonumber),
                "Area": ($area | tonumber),
                "Peak_Dynamic": ($peak | tonumber),
                "Runtime_Dynamic": ($runtime | tonumber),
                "Subthreshold_Leakage": ($leak | tonumber)
            }
        }'
done | jq -s 'add'