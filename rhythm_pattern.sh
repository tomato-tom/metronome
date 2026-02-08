#!/bin/bash
# リズムパターンを生成

# １拍４音のパターン
patterns=(
    0000 0001 0010 0011
    0100 0101 0110 0111
    1000 1001 1010 1011  # head
    1100 1101 1110 1111
)

# １拍3音のパターン
triplets=(
    000 001
    010 011
    100 101      # head
    110 111
)

generate_pattern() {
    local head_pattern
    local head_patterns=()
    local rest

    # -t オプションで3連符モード
    if [[ ${1:-} = -t ]]; then
        patterns=("${triplets[@]}")
        shift
    fi
    local beats=${1:-2}

    local n=${#patterns[@]}
    # 3番目のクォーター
    head_patterns=("${patterns[@]:$((n / 2)):$((n / 4))}")
    head_pattern=$(shuf -n 1 -e "${head_patterns[@]}")
    
    # 残りをランダムに選択（末尾の空白は tr で処理）
    rest=$(shuf -n $((beats - 1)) -e "${patterns[@]}" | tr '\n' ' ')
    
    echo "$head_pattern $rest"
}

generate_pattern "$@"
