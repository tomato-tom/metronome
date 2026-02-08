# metronome

## メトロノーム
metronome.sh

## フレットボード・クイズ
fretboard_quiz.sh

## リズムパターン生成

ランダム生成
rhythm_pattern.sh

アルゴリズム生成
euclidean_rhythm.py


## beepのセットアップ

```
# インストール
sudo apt install beep

# PCスピーカー有効化（一時的）
sudo modprobe pcspkr

# 永続化する場合
sudo vi /etc/modules-load.d/pcspkr.conf
# コメントアウト
#blacklist pcspkr
```
