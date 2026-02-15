# 音声ツール

PythonでMIDI、WAVE、サウンド関連の処理を行うためのライブラリ

- MIDI通信のみ → python-rtmidi または mido
- MIDIファイル解析 → pretty_midi
- シンプルなWAV読み書き → wave (標準) または soundfile
- オーディオ編集・変換 → pydub
- リアルタイム録音/再生 → pyaudio
- 音楽分析・研究 → librosa
- ゲーム開発 → pygame.mixer

## MIDI関連ライブラリ

### python-rtmidi
- リアルタイムMIDI入出力のためのライブラリ
- マルチプラットフォーム対応（Windows, macOS, Linux）
- MIDIデバイスとの通信に特化

```python
import rtmidi
midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()
```

### mido
- MIDIファイルの読み書き、リアルタイム通信に対応
- シンプルで使いやすいAPI
- バックエンドとしてpython-rtmidiなどを利用可能

```python
from mido import MidiFile, MidiTrack, Message
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)
track.append(Message('note_on', note=64, velocity=64, time=32))
```

### pretty_midi
- MIDIファイルの解析と操作に特化
- ピアノロール表現への変換機能
- 機械学習向けのデータ処理に便利

```python
import pretty_midi
midi_data = pretty_midi.PrettyMIDI('song.mid')
```

## WAVE/オーディオファイル関連ライブラリ

### wave (標準ライブラリ)
- Python標準ライブラリ
- WAVファイルの読み書き基本機能
- シンプルな操作が必要な場合に便利

```python
import wave
with wave.open('sound.wav', 'rb') as wav:
    frames = wav.readframes(wav.getnframes())
```

### pydub
- シンプルで直感的なAPI
- 様々なオーディオフォーマットに対応（ffmpeg必要）
- オーディオの編集、エフェクト処理が容易

```python
from pydub import AudioSegment
sound = AudioSegment.from_file("song.mp3", format="mp3")
sound.export("output.wav", format="wav")
```

### soundfile
- libsndfileをベースにした高性能ライブラリ
- WAV, FLAC, OGGなど多くのフォーマットに対応
- NumPy配列との相互変換が容易

```python
import soundfile as sf
data, samplerate = sf.read('file.wav')
sf.write('new_file.wav', data, samplerate)
```

## サウンド再生/録音ライブラリ

### pygame.mixer
- pygameライブラリのサウンド機能
- 複数サウンドの同時再生
- ゲーム開発などでよく使用

```python
import pygame
pygame.mixer.init()
sound = pygame.mixer.Sound('sound.wav')
sound.play()
```

### pyaudio
- PortAudioライブラリのバインディング
    - portaudio19-dev(debian)
- 低レベルなオーディオ入出力制御
- リアルタイム処理や録音機能に強い

```python
import pyaudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
```

### simpleaudio
- WAVファイルの再生に特化したシンプルなライブラリ
- 依存関係が少なく軽量
- 基本的な再生機能のみ必要なら最適

```python
import simpleaudio as sa
wave_obj = sa.WaveObject.from_wave_file("sound.wav")
play_obj = wave_obj.play()
```

## 音楽情報処理ライブラリ

###. librosa
- 音楽・オーディオ分析のための強力なライブラリ
- 特徴量抽出、スペクトル分析、時間周波数変換など
- 研究用途や機械学習プロジェクトで人気

```python
import librosa
y, sr = librosa.load('audio.mp3')
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
```

## FluidSynth

SoundFont 形式の音源を使用してMIDIファイルをリアルタイムでオーディオに変換するソフトウェアシンセサイザー
pyfluidsynth

## FFmpeg
マルチメディア処理のための強力なフレームワークで、音声・動画の変換、編集、ストリーミングなどが可能
ffmpeg-python

