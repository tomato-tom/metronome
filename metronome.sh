#!/bin/bash
# metronome.sh

bpm=${1:-120}
bars=${2:-4}
interval=$(echo "scale=3; 60/$bpm" | bc)

echo "BPM: $bpm (${interval}s per beat)"
echo "Bars: $bars"
echo "Press Ctrl+C to stop"

trap 'echo -e "\nStopped"; exit' INT

current_bar=1

while [ $bars -gt 0 ]; do
    echo -en "== Bar: $current_bar ==\r"
    echo -ne '\a'
    sleep $interval

    ((bars--))
    ((current_bar++))
done
