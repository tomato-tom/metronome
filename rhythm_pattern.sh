#!/bin/bash
# リズムパターンを生成

# １拍４音のパターン
patterns=(
    0000
    0001
    0010
    0011
    0100
    0101
    0110
    0111
    1000
    1001
    1010
    1011
    1100
    1101
    1110
    1111
)

# １拍3音のパターン
triplets=(
    000
    001
    010
    011
    100
    101
    110
    111
)

generate_pattern() {
    local first_pattern=
    local pattern=

    if [[ $1 = -t ]]; then
        patterns=("${triplets[@]}")
        shift
    fi

    local beats=${1:-2}

    # 最初はダウンビートから
    length="${#patterns[@]}"
    first_pattern="$(shuf -n 1 -e ${patterns[@]:$((length / 2))})"
    # 残りのパターンをつなげる
    pattern="$first_pattern $(shuf -n $((beats - 1)) -e ${patterns[@]} | tr '\n' ' ')"

    echo "$pattern"
}

generate_pattern "$@"

