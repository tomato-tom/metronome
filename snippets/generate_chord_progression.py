import numpy as np
import pyaudio
import mido
from mido import MidiFile, MidiTrack, Message

# 設定
SAMPLE_RATE = 44100
BPM = 120
BEAT_LENGTH = 60 / BPM  # 1拍の長さ（秒）
NOTE_VELOCITY = 80

# ノート番号定義（C4 = 60）
NOTE_NUMBERS = {
    'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
    'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
    'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
}

# 周波数テーブル（A4=440Hz）
def note_to_freq(note):
    return 440 * (2 ** ((note - 69) / 12))

# ============================================
# 1. 簡易再生（サイン波）
# ============================================
def play_chord(chord_notes, duration=1.0):
    """コードをサイン波で鳴らす（chord_notes: ノート番号のリスト）"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.zeros_like(t)
    
    for note in chord_notes:
        freq = note_to_freq(note)
        wave += np.sin(2 * np.pi * freq * t)
    
    # 正規化
    wave = wave / (len(chord_notes) + 1)
    
    # PyAudio再生
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True)
    stream.write(wave.astype(np.float32).tobytes())
    stream.close()
    p.terminate()

def play_progression(chord_list, beats_per_chord=4):
    """コード進行を再生"""
    for chord_name in chord_list:
        notes = parse_chord(chord_name)
        print(f"鳴らす: {chord_name} {notes}")
        play_chord(notes, BEAT_LENGTH * beats_per_chord)

def parse_chord(chord_name):
    """C, Am, F, G7 などをノート番号リストに変換（簡易版）"""
    root = chord_name[0].upper()
    root_num = NOTE_NUMBERS[root]
    
    if 'm' in chord_name:  # マイナー
        return [root_num, root_num + 3, root_num + 7]
    elif '7' in chord_name:  # セブンス
        return [root_num, root_num + 4, root_num + 7, root_num + 10]
    else:  # メジャー
        return [root_num, root_num + 4, root_num + 7]

# ============================================
# 2. MIDIファイル保存
# ============================================
def save_as_midi(chord_list, filename="output.mid", beats_per_chord=4):
    """コード進行をMIDIファイルに保存"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_chord = ticks_per_beat * beats_per_chord
    
    for chord_name in chord_list:
        notes = parse_chord(chord_name)
        
        # ノートオン
        for note in notes:
            track.append(Message('note_on', note=note, velocity=NOTE_VELOCITY, time=0))
        
        # ノートオフ（次のコードの前に）
        for note in notes:
            track.append(Message('note_off', note=note, velocity=0, time=ticks_per_chord))
    
    mid.save(filename)
    print(f"MIDI保存: {filename}")

# ============================================
# 3. 実行例
# ============================================
if __name__ == "__main__":
    # テスト進行
    progression = ["C", "Am", "F", "G7"]
    
    # まず簡易再生
    print("--- 簡易再生開始 ---")
    play_progression(progression)
    
    # 気に入ったらMIDI保存
    ans = input("\nMIDIファイルを保存しますか？ (y/n): ")
    if ans.lower() == 'y':
        save_as_midi(progression)
        print("完了")
