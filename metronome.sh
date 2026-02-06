#!/bin/bash

bpm=${1:-120}
beats=${2:-4}
bars=${3:-99}
interval=$(echo "scale=3; 60/$bpm" | bc)

echo "BPM: $bpm (${interval}s per beat)"
echo "Space to pause/resume, q to quit"
echo

trap 'kill $play_pid 2>/dev/null; echo -e "\nStopped"; exit' INT

play() {
    local bar=1 beat=1
    while [ $bar -le $bars ]; do
        beat=1
        while [ $beat -le $beats ]; do
            # 一時停止ファイルをチェック
            while [ -f /tmp/metronome_pause ]; do
                sleep 0.1
            done
            
            echo -en "== Bar: $bar Beat: $beat ==\r"
            beep -l 60 &
            sleep $interval
            ((beat++))
        done
        ((bar++))
    done
}

play &
play_pid=$!

paused=false
while :; do
    read -rsn1 key
    if [[ -z $key ]]; then
        if $paused; then
            rm -f /tmp/metronome_pause
            paused=false
            echo -ne "\rResumed...              \r"
        else
            touch /tmp/metronome_pause
            paused=true
            echo -ne "\rPaused...               \r"
        fi
    elif [[ $key == 'q' ]]; then
        kill $play_pid 2>/dev/null
        rm -f /tmp/metronome_pause
        echo -e "\nQuit"
        exit
    fi
done
