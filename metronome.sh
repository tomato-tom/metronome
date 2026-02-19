#!/bin/bash

bpm=${1:-120}
beats=${2:-4}
bars=${3:-99}

# BPMを表示する関数
show_bpm() {
    echo -ne "\rBPM: $bpm ($(echo "scale=3; 60/$bpm" | bc)s per beat) - Bar: ? Beat: ?\r"
}

# 初期表示
show_bpm
echo
echo "Controls:"
echo "  u/d : BPM +/- 1"
echo "  U/D : BPM +/- 10%"
echo "  Space: pause/resume"
echo "  q: quit"
echo

trap 'kill $play_pid 2>/dev/null; rm -f /tmp/metronome_pause; echo -e "\nStopped"; exit' INT

play() {
    local bar=1 beat=1
    while [ $bar -le $bars ]; do
        beat=1
        while [ $beat -le $beats ]; do
            # 一時停止ファイルをチェック
            while [ -f /tmp/metronome_pause ]; do
                sleep 0.1
            done
            
            echo -ne "\rBPM: $bpm ($(echo "scale=3; 60/$bpm" | bc)s per beat) - Bar: $bar Beat: $beat  \r"
            beep -l 60 &
            
            # intervalを動的に計算（BPM変更に対応）
            interval=$(echo "scale=3; 60/$bpm" | bc)
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
        # Space key
        if $paused; then
            rm -f /tmp/metronome_pause
            paused=false
        else
            touch /tmp/metronome_pause
            paused=true
            echo -ne "\rPaused... BPM: $bpm ($(echo "scale=3; 60/$bpm" | bc)s per beat)               \r"
        fi
    elif [[ $key == 'u' ]]; then
        # u: BPM +1
        bpm=$((bpm + 1))
        show_bpm
    elif [[ $key == 'd' ]]; then
        # d: BPM -1
        if [ $bpm -gt 1 ]; then
            bpm=$((bpm - 1))
        fi
        show_bpm
    elif [[ $key == 'U' ]]; then
        # U: BPM +10% (小数点以下切り捨て)
        bpm=$(echo "$bpm * 1.1 / 1" | bc)
        show_bpm
    elif [[ $key == 'D' ]]; then
        # D: BPM -10% (小数点以下切り捨て)
        if [ $bpm -gt 10 ]; then
            bpm=$(echo "$bpm * 0.9 / 1" | bc)
        fi
        show_bpm
    elif [[ $key == 'q' ]]; then
        kill $play_pid 2>/dev/null
        rm -f /tmp/metronome_pause
        echo -e "\nQuit"
        exit
    fi
done
