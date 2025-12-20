#!/bin/bash
# metronome_swing.sh

# 環境チェック
dpkg -l beep > /dev/null 2>&1 || exit 1
lsmod | grep pcspkr >/dev/null 2>&1 || sudo modprobe pcspkr
echo $? || exit 1

# 設定
bpm=${1:-120}
bars=${2:-4}
swing=${3:-3}  # 2=ストレート, 3=3連符スイング, 4=4連符スイング
interval=$(echo "scale=6; 60/$bpm" | bc)

echo "BPM: $bpm"
echo "Bars: $bars"
echo "Swing: $swing"

if [ "$swing" == 2 ]; then
    # Straight
    downbeat_interval=$(echo "scale=6; $interval/2" | bc)
    upbeat_interval=$downbeat_interval
else
    # Swing
    downbeat_interval=$(echo "scale=6; $interval/$swing*($swing-1)" | bc)
    upbeat_interval=$(echo "scale=6; $interval-$downbeat_interval" | bc)
fi
# 2以下は？

trap 'echo -e "\nStopped"; exit' INT

freq=440
length=40
current_bar=1

while [ $bars -gt 0 ]; do
    echo -en "== Bar: $current_bar ==\r"
    
    beep -f $freq -l $length -d 0 &
    sleep $downbeat_interval

    beep -f $freq -l $length -d 0 &
    sleep $upbeat_interval

    ((bars--))
    ((current_bar++))
done

echo
