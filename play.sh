#!/bin/bash
# リズムパターンプレイヤー

# デフォルト設定
BPM=120
FREQ=440        # Hz (A4)
DURATION=80     # ms per note
MODE=quad       # quad (4分音符4分割) or triplet (3連符)

# beepが利用可能か確認
if ! type beep &>/dev/null; then
    echo "'beep' command not found"
    exit 1
fi

# オプション解析
while getopts "b:f:t" opt; do
  case $opt in
    b) BPM=$OPTARG ;;
    f) FREQ=$OPTARG ;;
    t) MODE=triplet ;;
    *) echo "Usage: $0 [-b BPM] [-f FREQUENCY] [-t]" >&2; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

# 入力取得（引数または標準入力）
if [[ -n "$1" ]]; then
    pattern="$*"
else
    read -r pattern
fi
echo $pattern

# 1拍のミリ秒数を計算
beat_ms=$(( 60000 / BPM ))

# 音符長さを計算
if [[ $MODE = triplet ]]; then
    note_ms=$(( beat_ms / 3 ))
else
    note_ms=$(( beat_ms / 4 ))
fi

play() {
    # パターンを1拍ずつ処理
    for beat in $pattern; do
        # 拍の開始時刻を記録（正確なタイミング制御のため）
        start_time=$(date +%s%N)
        
        # 1拍内の各ビットを処理
        for (( i=0; i<${#beat}; i++ )); do
            bit="${beat:$i:1}"
            
            if [[ "$bit" = "1" ]]; then
                beep -f $FREQ -l $DURATION -D 0 &>/dev/null
            fi
            
            # 次の音符まで待機（正確なタイミングのため残り時間を計算）
            elapsed=$(( ($(date +%s%N) - start_time) / 1000000 ))
            target_time=$(( (i + 1) * note_ms ))
            sleep_time=$(( target_time - elapsed ))
            
            if [[ $sleep_time -gt 0 ]]; then
                sleep "$(awk "BEGIN {printf \"%.3f\", $sleep_time / 1000.0}")"
            fi
        done
    done
}

for i in {1..4}; do
    play
done
