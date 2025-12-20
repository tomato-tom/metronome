#!/bin/bash
# metronome_stats.sh
# 計測機能付きメトロノーム

bpm=${1:-120}
interval=$(echo "scale=6; 60/$bpm" | bc)

trap 'echo -e "\n\nMetronome stopped after $count beats";
      end_time=$(date +%s.%N);
      total_time=$(echo "$end_time - $start_time" | bc);
      expected_time=$(echo "$interval * ($count-1)" | bc);
      
      # 誤差計算
      error=$(echo "scale=3; $total_time - $expected_time" | bc);
      avg_error_ms=$(echo "scale=3; ($error / ($count-1)) * 1000" | bc | sed 's/^-//');
      
      echo "Actual: ${total_time}s";
      echo "Expected: ${expected_time}s";
      echo "Drift: ${error}s";
      echo "Avg drift per beat: ${avg_error_ms}ms";
      exit' INT

echo "Metronome started with BPM: ${bpm} (interval: ${interval}s)"
echo "Press Ctrl+C to stop"

start_time=$(date +%s.%N)
current_bar=1

while :; do
    echo -en "== Bar: $current_bar ==\r"
    echo -ne '\a' &
    sleep $interval

    ((count++))
    ((current_bar++))
done
