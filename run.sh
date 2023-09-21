#!/bin/bash
# read lines in accounts.csv
filename="proxies.txt"
lines=$(wc -l < "$filename")
echo "-- There are $lines lines in $filename"

read -p "Enter total number of bots: " x
read -p "Enter number of bots per batch: " batchSize
read -p "Enter delay in seconds: " delay

jobs=()

for ((i = 0; i < x; i += batchSize)); do
    for ((j = i; j < i + batchSize && j <= x; j++)); do
        python3 "outlook.py" "$j" "$batchSize" &
        jobs+=($!)
    done
    for job in "${jobs[@]}"; do
        wait "$job"
    done
    jobs=()
    if ((i + batchSize < x)); then
        echo "Waiting for $delay seconds before next batch..."
        sleep "$delay"
    fi
done
