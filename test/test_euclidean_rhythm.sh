#!/bin/bash
# euclidean_rhythm.pyのテスト

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel)"
MAX=${1:-8}

for (( i=1; i<=$MAX; i++ )); do
    for (( j=1; j<=i; j++ )); do
        python "$PROJECT_ROOT/euclidean_rhythm.py" $j $i
    done
done

