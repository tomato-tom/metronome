#!/bin/bash

# Euclidean Rhythm Generator
# E(k, n) = k beats distributed over n steps

euclidean_rhythm() {
    local k=$1  # number of beats
    local n=$2  # number of steps
    
    if [ $k -gt $n ] || [ $k -eq 0 ]; then
        echo "Error: must be k <= n and k >= 1"
        return 1
    fi
    
    echo "E($k, $n) - $k beats in $n steps"
    echo "================================"
    
    # Initialize arrays
    declare -a pattern
    
    # Start with k ones and (n-k) zeros
    for ((i=0; i<k; i++)); do
        pattern[$i]="1"
    done
    for ((i=k; i<n; i++)); do
        pattern[$i]="0"
    done
    
    echo -n "Initial: ["
    printf "%s" "${pattern[@]}"
    echo "]"
    
    # Bjorklund's algorithm (equivalent to Euclidean algorithm)
    # Use arrays to store groups
    declare -a groups
    declare -a group_counts
    
    # Initialize: k groups of "1", (n-k) groups of "0"
    groups[0]="1"
    group_counts[0]=$k
    
    if [ $((n-k)) -gt 0 ]; then
        groups[1]="0"
        group_counts[1]=$((n-k))
    fi
    
    # Apply Bjorklund's algorithm
    while [ ${#groups[@]} -gt 1 ] && [ ${group_counts[${#groups[@]}-1]} -gt 1 ]; do
        local num_groups=${#groups[@]}
        local last_idx=$((num_groups - 1))
        local prev_idx=$((num_groups - 2))
        
        # Number of pairs we can make
        local pairs=${group_counts[$prev_idx]}
        if [ ${group_counts[$last_idx]} -lt $pairs ]; then
            pairs=${group_counts[$last_idx]}
        fi
        
        # Create new combined group
        local new_group="${groups[$prev_idx]}${groups[$last_idx]}"
        
        # Calculate remainders
        local remainder_prev=$((${group_counts[$prev_idx]} - pairs))
        local remainder_last=$((${group_counts[$last_idx]} - pairs))
        
        # Rebuild arrays
        declare -a new_groups
        declare -a new_counts
        local idx=0
        
        # Add everything before prev_idx
        for ((i=0; i<prev_idx; i++)); do
            new_groups[$idx]="${groups[$i]}"
            new_counts[$idx]=${group_counts[$i]}
            ((idx++))
        done
        
        # Add the paired groups
        new_groups[$idx]="$new_group"
        new_counts[$idx]=$pairs
        ((idx++))
        
        # Add remainders
        if [ $remainder_prev -gt 0 ]; then
            new_groups[$idx]="${groups[$prev_idx]}"
            new_counts[$idx]=$remainder_prev
            ((idx++))
        fi
        
        if [ $remainder_last -gt 0 ]; then
            new_groups[$idx]="${groups[$last_idx]}"
            new_counts[$idx]=$remainder_last
            ((idx++))
        fi
        
        groups=("${new_groups[@]}")
        group_counts=("${new_counts[@]}")

        read -n1 # debug
    done
    
    # Build final pattern
    local result=""
    for ((i=0; i<${#groups[@]}; i++)); do
        for ((j=0; j<${group_counts[$i]}; j++)); do
            result="${result}${groups[$i]}"
        done
    done
    
    echo -n "Result:  ["
    echo -n "$result"
    echo "]"
    echo ""
}

# ユーザー入力版
if [ $# -eq 2 ]; then
    echo "=== Custom Input ==="
    euclidean_rhythm $1 $2
else
    # テスト例
    echo "=== Euclidean Rhythm Examples ==="
    echo ""

    # Example 1: [1001010010100] - Cuban tresillo
    euclidean_rhythm 3 8

    # Example 2: [10010100] 
    euclidean_rhythm 3 7

    # Example 3: [1001001001001] - The famous E(5,13)
    euclidean_rhythm 5 13

    # Example 4: [10101010]
    euclidean_rhythm 4 8

    # Example 5: [1010010100101]
    euclidean_rhythm 5 12
fi
