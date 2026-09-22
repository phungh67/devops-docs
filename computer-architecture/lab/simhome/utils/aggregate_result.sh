#!/bin/bash

BASE_RESULT=$1
AGGREGATE_DIR=$2

if [[ -z "$BASE_RESULT" || -z "$AGGREGATE_DIR" ]]; then
    echo "[ERROR] Missing required arguments." >&2
    echo "[INFO] Usage: $0 <path_to_base_output> <path_to_cache_sweeping_directory>." >&2
    exit 1
fi

if [[ ! -f "$BASE_RESULT" ]]; then
    echo "[ERROR] The base result file is invalid or missing." >&2
    exit 1
fi

echo "[INFO] Extracting baseline metrics from $BASE_RESULT..."
QSORT_BASE=$(jq -r '.qsort.sim_cycle' "$BASE_RESULT")
GSM_BASE=$(jq -r '.["gsm-untoast"].sim_cycle' "$BASE_RESULT")
JPEG_BASE=$(jq -r '.["jpeg-cjpeg"].sim_cycle' "$BASE_RESULT")

for dir in "$AGGREGATE_DIR"/*; do
    if [[ ! -d "$dir" ]]; then continue; fi
    
    FILE_PATH="${dir}/sim_out.json"
    echo "[INFO] Processing output in config: $FILE_PATH..."
    
    if [[ ! -f "$FILE_PATH" ]]; then
        echo "[WARN] Output file not found in $dir. Skipping..." >&2
        continue
    fi

    QSORT_NEW=$(jq -r '.qsort.sim_cycle' "$FILE_PATH")
    GSM_NEW=$(jq -r '.["gsm-untoast"].sim_cycle' "$FILE_PATH")
    JPEG_NEW=$(jq -r '.["jpeg-cjpeg"].sim_cycle' "$FILE_PATH")

    read QS_SPEEDUP GSM_SPEEDUP JPEG_SPEEDUP GEO_MEAN <<< $(awk \
        -v qb="$QSORT_BASE" -v qn="$QSORT_NEW" \
        -v gb="$GSM_BASE" -v gn="$GSM_NEW" \
        -v jb="$JPEG_BASE" -v jn="$JPEG_NEW" 'BEGIN { 
            qs = qb / qn
            gs = gb / gn
            js = jb / jn
            gm = (qs * gs * js) ^ (1/3)
            printf "%.6f %.6f %.6f %.6f\n", qs, gs, js, gm 
        }')

    jq --argjson qs "$QS_SPEEDUP" \
       --argjson gs "$GSM_SPEEDUP" \
       --argjson js "$JPEG_SPEEDUP" \
       --argjson gm "$GEO_MEAN" \
       '.qsort.speedup = $qs | .["gsm-untoast"].speedup = $gs | .["jpeg-cjpeg"].speedup = $js | .aggregate_geometric_mean = $gm' \
       "$FILE_PATH" > "${FILE_PATH}.tmp" && mv "${FILE_PATH}.tmp" "$FILE_PATH"

    echo "[SUCCESS] Injected speedup metrics into $FILE_PATH"
done

echo "[INFO] All configurations successfully aggregated."