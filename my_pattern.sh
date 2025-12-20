#!/bin/bash

bpm=${1:-120}
bars=${2:-4}

rythm() {
	local multiplier=${1:-1}
	local cur_bpm=$((bpm * multiplier))
	local beat_count=$((bars * multiplier))

	bash metronome.sh $cur_bpm $beat_count
}

# カウント
rythm

# リズムパターン
rythm 2
rythm 3
rythm 4
rythm

