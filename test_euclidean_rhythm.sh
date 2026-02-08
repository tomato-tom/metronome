#!/bin/bash
# euclidean_rhythm.pyのテスト

max=${1:-8}

for (( i=1; i<=$max; i++ )); do
    for (( j=1; j<=i; j++ )); do
        python euclidean_rhythm.py $j $i
    done
done

