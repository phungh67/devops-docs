#!/bin/bash

if [ "$#" -lt 1 ]; then
    echo -e "\e[31mUsage: $0 <Simulation Directory>\e[0m" >&2
    exit 1
fi

Sim_DIR=$1
benchmarks=( dijkstra qsort string_search gsm jpeg )

echo -e "\e[36m[INFO] Starting JSON parsing for directory: $Sim_DIR\e[0m" >&2

for b in "${benchmarks[@]}"; do
    sim_out="$Sim_DIR/$b/sim.out"
    power_out="$Sim_DIR/$b/power.txt"
    
    # Initialize defaults to 0 to prevent jq 'tonumber' crashes
    insn=0
    cycles=0
    area=0
    peak_dyn=0
    runtime_dyn=0
    leakage=0

    # ---------------------------------------------------------
    # Performance Parsing
    # ---------------------------------------------------------
    if [ ! -f "$sim_out" ]; then
        echo -e "\e[33m[WARN] $sim_out missing for $b. Defaulting to 0.\e[0m" >&2
    else
        insn=$(grep -m1 "Instructions" "$sim_out" | awk '{print $3}')
        cycles=$(grep -m1 "Cycles" "$sim_out" | awk '{print $3}')
        
        insn=${insn:-0}
        cycles=${cycles:-0}
    fi

    # ---------------------------------------------------------
    # Power Parsing
    # ---------------------------------------------------------
    if [ ! -f "$power_out" ]; then
        echo -e "\e[33m[WARN] $power_out missing for $b. Defaulting to 0.\e[0m" >&2
    else
        # Extract the Core section once into a variable (no temp files needed)
        core_stats=$(grep -A6 "Core:" "$power_out")
        
        # Extract specific power metrics using NF-1 (second to last column)
        area=$(echo "$core_stats" | grep -m1 "Area =" | awk '{print $(NF-1)}')
        peak_dyn=$(echo "$core_stats" | grep -m1 "Peak Dynamic =" | awk '{print $(NF-1)}')
        runtime_dyn=$(echo "$core_stats" | grep -m1 "Runtime Dynamic =" | awk '{print $(NF-1)}')
        leakage=$(echo "$core_stats" | grep -m1 "Subthreshold Leakage =" | awk '{print $(NF-1)}')
        
        area=${area:-0}
        peak_dyn=${peak_dyn:-0}
        runtime_dyn=${runtime_dyn:-0}
        leakage=${leakage:-0}
    fi

    # ---------------------------------------------------------
    # JSON Emission
    # ---------------------------------------------------------
    # Emit a standalone JSON object for this benchmark to stdout
    jq -n \
        --arg test "$b" \
        --arg insn "$insn" \
        --arg cyc "$cycles" \
        --arg area "$area" \
        --arg peak "$peak_dyn" \
        --arg runtime "$runtime_dyn" \
        --arg leak "$leakage" \
        '{
            ($test): {
                "Instructions": ($insn | tonumber),
                "Cycles": ($cyc | tonumber),
                "Area": ($area | tonumber),
                "Peak_Dynamic": ($peak | tonumber),
                "Runtime_Dynamic": ($runtime | tonumber),
                "Subthreshold_Leakage": ($leak | tonumber)
            }
        }'
done | jq -s 'add'