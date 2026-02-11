
fretboard_quiz.sh
弦と音名指定 -> フレット番号
ギター・ウクレレ
変則チューニング

metronome.sh
ホットキーでBPM変更
振り子ぽいアニメーション

## リズムパターン生成
rhythm_pattern.sh

### 各拍の役割

beat 1
beat 2
beat 3
beat 4

### ユークリッドリズム
リズム生成アルゴリズムの一種



### 難易度自己評価
- pattern
    - 1011 0101
    - 1101 0001 1010
    - 1100 0110 0001 0011
- difficulty
    - easy
    - hard

データ形式例
```json
{
  "date": "2024-01-15_14:30",
  "pattern": "1101 0001 1010",
  "difficulty": "hard",
  "type": "single_stroke",
  "metadata": {
    "bpm": 120,
    "bars": 3
  }
}
```

### 練習パターンの例
single_stroke:
    1 - シングルストローク
    0 - 休符
double_stroke:
    1 - ダブルストローク
    0 - シングルストローク
accent:
    1 - アクセント
    0 - 軽く
flam
    1 - フラム
    0 - シングルストローク

### ドラムパターン生成

８ビート
HH - 1010 1010 1010 1010
SD - 0000 1000 0000 1000
BD - 1000 0000 1010 0000

フィル
SY - 1000 0010 0000 1000
SD - 0011 1100 1111 0000
BD - 1000 0010 1000 1000

音源は？

metronome_stats.sh
metronome_swing.sh

