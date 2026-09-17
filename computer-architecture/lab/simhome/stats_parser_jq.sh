#!/bin/bash
DIR=$1
CFG=$2
OUT_DIR=$3

# excluded dijkstra and stringsearch-cabce
benchspecs=( qsort gsm-untoast jpeg-cjpeg )

# check and raise a warning for default output value
if [ -z $3 ]; then
    echo "[?] WARNING: the output file was not specified, fallback to default value."
    echo "[!] INFO: the output file name should be simulation_${DIR}_${CFG}_out.json."
    OUT_DIR="simulation_${DIR}_${CFG}_out.json"
fi

for BENCHMARK in "${benchspecs[@]}"
do
    FILE="configs/$DIR/Stats_${CFG}_${BENCHMARK}.txt"
    
    # Saftey check: skip to the next benchmark if the output file is missing
    [ ! -f "$FILE" ] && continue

    # Extract values, using -m1 to stop reading after the first match
    sim_num_insn=$(grep -m1 "sim_num_insn" "$FILE" | awk '{print $2}')
    sim_cycle=$(grep -m1 "sim_cycle" "$FILE" | awk '{print $2}')
    sim_CPI=$(grep -m1 "sim_CPI" "$FILE" | awk '{print $2}')
    il1_misses=$(grep -m1 "il1.misses" "$FILE" | awk '{print $2}')
    dl1_misses=$(grep -m1 "dl1.misses" "$FILE" | awk '{print $2}')

    # Fallback to 0 if variables are empty to prevent jq tonumber errors
    sim_num_insn=${sim_num_insn:-0}
    sim_cycle=${sim_cycle:-0}
    sim_CPI=${sim_CPI:-0}

    # Calculate MPI, guarding against division by zero
    if [ -z "$il1_misses" ] || [ "$sim_num_insn" -eq 0 ]; then
        mpi_il1=0
        mpi_dl1=0
    else 
        mpi_il1=$(awk "BEGIN {printf \"%.5f\",${il1_misses}/${sim_num_insn}}")
        mpi_dl1=$(awk "BEGIN {printf \"%.5f\",${dl1_misses}/${sim_num_insn}}")
    fi

    # Emit a standalone JSON object for this benchmark
    jq -n \
        --arg test "$BENCHMARK" \
        --arg insn "$sim_num_insn" \
        --arg cyc "$sim_cycle" \
        --arg cpi "$sim_CPI" \
        --arg mpi_il1 "${mpi_il1/,/.}" \
        --arg mpi_dl1 "${mpi_dl1/,/.}" \
        '{
            ($test): {
                "sim_num_insn": ($insn | tonumber),
                "sim_cycle": ($cyc | tonumber),
                "sim_CPI": ($cpi | tonumber),
                "mpi_il1": ($mpi_il1 | tonumber),
                "mpi_dl1": ($mpi_dl1 | tonumber)
            }
        }'
done | jq -s 'add' >> ${OUT_DIR}