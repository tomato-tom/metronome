#!/bin/bash

bpm=${1:-120}
beats=${2:-4}
bars=${3:-99}

FREQ=880
LEN=60
PAUSE=/tmp/metronome_pause

# FIFOの作成
FIFO=/tmp/metronome_bpm.fifo
rm -f $FIFO
mkfifo $FIFO

# 初期表示
echo "Controls:"
echo "  u/d : BPM +/- 1"
echo "  U/D : BPM +/- 10%"
echo "  Space: pause/resume"
echo "  q: quit"
echo

trap 'kill $play_pid 2>/dev/null; rm -f $PAUSE $FIFO; echo -e "\nStopped"; exit' INT

play() {
    local bar=1 beat=1
    local current_bpm=$bpm
    local next_beat_time=0
    
    # 非ブロッキングでFIFOを開く
    exec 3<>$FIFO

    # BPM表示
    show_bpm() { printf "\rBPM: %d - Bar: %d Beat: %d  " $current_bpm $bar $beat; }

    # BPM変更をチェック
    check_bpm() {
        if read -t 0 <&3; then
            read -r new_bpm <&3
            if [[ -n $new_bpm ]]; then
                current_bpm=$new_bpm
                show_bpm
            fi
        fi
    }
    
    # 初期表示
    show_bpm
    
    # 開始時間を取得（エポック秒 + ナノ秒）
    start_time=$(date +%s.%N)
    
    while [ $bar -le $bars ]; do
        beat=1
        while [ $beat -le $beats ]; do
            # ビートを鳴らす
            show_bpm
            beep -f $FREQ -l $LEN &
            
            # 次のビートの時間を計算
            interval=$(echo "scale=3; 60/$current_bpm" | bc)
            next_beat_time=$(echo "$next_beat_time + $interval" | bc)
            
            # 次のビートの時間になるまで待機
            while true; do
                # 現在時間を取得
                current_time=$(echo "$(date +%s.%N) - $start_time" | bc)
                
                # 一時停止チェック
                while [ -f $PAUSE ]; do
                    # ポーズ中は時間を止める（開始時間を調整）
                    sleep 0.1
                    start_time=$(echo "$start_time + 0.1" | bc)
                    current_time=$(echo "$(date +%s.%N) - $start_time" | bc)
                    check_bpm
                done
                
                # BPM変更チェック
                check_bpm
                
                # 次のビートの時間を過ぎていたら break
                if (( $(echo "$current_time >= $next_beat_time" | bc -l) )); then
                    break
                fi
                
                # 少し待機
                sleep 0.01
            done
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

# 親プロセスはキー入力処理のみ
while :; do
    read -rsn1 key
    case $key in
        '') # Space key
            if $paused; then
                rm -f $PAUSE
                paused=false
            else
                touch $PAUSE
                paused=true
            fi
            ;;
        u) # BPM +1
            bpm=$((bpm + 1))
            echo $bpm > $FIFO &
            ;;
        d) # BPM -1
            if [ $bpm -gt 1 ]; then
                bpm=$((bpm - 1))
                echo $bpm > $FIFO &
            fi
            ;;
        U) # BPM +10%
            bpm=$(echo "$bpm * 1.1 / 1" | bc)
            echo $bpm > $FIFO &
            ;;
        D) # D: BPM -10%
            if [ $bpm -gt 10 ]; then
                bpm=$(echo "$bpm * 0.9 / 1" | bc)
                echo $bpm > $FIFO &
            fi
            ;;
        q)
            kill $play_pid 2>/dev/null
            rm -f $PAUSE $FIFO
            echo -e "\nQuit"
            exit
            ;;
    esac
done
