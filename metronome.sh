#!/bin/bash

bpm=${1:-120}
beats=${2:-4}
bars=${3:-99}
freq=880
len=60

# FIFOの作成
FIFO=/tmp/metronome_bpm.fifo
rm -f $FIFO
mkfifo $FIFO

# 初期表示
show_bpm
echo
echo "Controls:"
echo "  u/d : BPM +/- 1"
echo "  U/D : BPM +/- 10%"
echo "  Space: pause/resume"
echo "  q: quit"
echo

trap 'kill $play_pid 2>/dev/null; rm -f /tmp/metronome_pause $FIFO; echo -e "\nStopped"; exit' INT

play() {
    local bar=1 beat=1
    local current_bpm=$bpm
    
    # 非ブロッキングでFIFOを開く
    exec 3<>$FIFO

    # BPMを表示
    show_bpm() {
        local bpm=$1
        local bar=$2
        local beat=$3
        echo -ne "\rBPM: $bpm - Bar: $bar Beat: $beat  \r"
    }

    # BPM変更をチェック
    check_bpm() {
        if read -t 0 <&3; then
            read -r new_bpm <&3
            if [[ -n $new_bpm ]]; then
                current_bpm=$new_bpm
                show_bpm $current_bpm $bar $beat
            fi
        fi
    }
    
    while [ $bar -le $bars ]; do
        beat=1
        while [ $beat -le $beats ]; do
            # 一時停止ファイルをチェック
            while [ -f /tmp/metronome_pause ]; do
                check_bpm
                sleep 0.1
            done
            
            check_bpm
            show_bpm $current_bpm $bar $beat
            beep -f $freq -l $len &
            
            # interval計算
            interval=$(echo "scale=3; 60/$current_bpm" | bc)
            sleep $interval
            ((beat++))
        done
        ((bar++))
    done
    
    # FIFOを閉じる
    exec 3<&-
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
        fi
    elif [[ $key == 'u' ]]; then
        # u: BPM +1
        bpm=$((bpm + 1))
        echo $bpm > $FIFO &
    elif [[ $key == 'd' ]]; then
        # d: BPM -1
        if [ $bpm -gt 1 ]; then
            bpm=$((bpm - 1))
            echo $bpm > $FIFO &
        fi
    elif [[ $key == 'U' ]]; then
        # U: BPM +10% (小数点以下切り捨て)
        bpm=$(echo "$bpm * 1.1 / 1" | bc)
        echo $bpm > $FIFO &
    elif [[ $key == 'D' ]]; then
        # D: BPM -10% (小数点以下切り捨て)
        if [ $bpm -gt 10 ]; then
            bpm=$(echo "$bpm * 0.9 / 1" | bc)
            echo $bpm > $FIFO &
        fi
    elif [[ $key == 'q' ]]; then
        kill $play_pid 2>/dev/null
        rm -f /tmp/metronome_pause $FIFO
        echo -e "\nQuit"
        exit
    fi
done
