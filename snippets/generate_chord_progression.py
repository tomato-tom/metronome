import numpy as np
import pyaudio
import mido
from mido import MidiFile, MidiTrack, Message
import json
import random
import play_wave_sound

# ============================================
# 設定
# ============================================
CONFIG = {
    "functions": ["T", "SD", "D"],
    "transition": {
        "T":  {"T": 0.4, "SD": 0.35, "D": 0.25},
        "SD": {"SD": 0.2, "T": 0.4,   "D": 0.4},
        "D":  {"D": 0.15, "T": 0.7,   "SD": 0.15}
    },
    "substitutions": {
        "T":  ["C", "Am", "Em"],
        "SD": ["F", "Dm7"],
        "D":  ["G", "G7", "Dm7"]
    },
    "change_rate": {
        "default": 0.7,
        "per_function": {
            "T": 0.6,
            "SD": 0.8,
            "D": 0.7
        }
    },
    "seventh_rules": {
        "mode": "specific",
        "specific_chords": ["G7", "Dm7"],
        "probability": 0.3
    },
    "bass_note_variation": {
        "enabled": False,  # 後で拡張
        "probability": 0.2
    }
}

# ============================================
# 生成エンジン
# ============================================
class ChordProgressionGenerator:
    def __init__(self, config):
        self.config = config
        self.functions = config["functions"]
        self.transition = config["transition"]
        self.subs = config["substitutions"]
        self.change_rate = config["change_rate"]
    
    def generate(self, bars=4, start_function="T"):
        """機能の並びを生成"""
        progression = []
        current = start_function
        last_chord = None
        
        for i in range(bars):
            # コードを割り当て
            candidates = self.subs[current]
            
            # 変化率に基づいて前回と同じコードを避ける
            if last_chord and len(candidates) > 1:
                rate = self.change_rate["per_function"].get(current, self.change_rate["default"])
                if random.random() > rate:
                    # 同じコードを継続
                    chord = last_chord
                else:
                    # 別のコードを選ぶ
                    chord = random.choice([c for c in candidates if c != last_chord])
            else:
                chord = random.choice(candidates)
            
            #progression.append((current, chord))
            progression.append(chord)
            last_chord = chord
            
            # 次の機能を選ぶ（最終小節は除く）
            if i < bars - 1:
                next_func = random.choices(
                    list(self.transition[current].keys()),
                    weights=list(self.transition[current].values())
                )[0]
                current = next_func
        
        print(progression) # debug
        return progression
    
    def pretty_print(self, progression):
        """コード進行を表示"""
        return " | ".join(progression)

# ============================================
# サウンドエンジン
# ============================================
SAMPLE_RATE = 44100
BPM = 120
BEAT_LENGTH = 60 / BPM

#NOTE_NUMBERS = {
#    'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
#    'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
#    'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
#}
#
#def note_to_freq(note):
#    return 440 * (2 ** ((note - 69) / 12))
#
#def parse_chord(chord_name):
#    """簡易コードパーサ"""
#    root = chord_name[0].upper()
#    root_num = NOTE_NUMBERS[root]
#    
#    if 'm' in chord_name and '7' in chord_name:  # m7
#        return [root_num, root_num + 3, root_num + 7, root_num + 10]
#    elif 'm' in chord_name:  # m
#        return [root_num, root_num + 3, root_num + 7]
#    elif '7' in chord_name:  # 7
#        return [root_num, root_num + 4, root_num + 7, root_num + 10]
#    else:  # M
#        return [root_num, root_num + 4, root_num + 7]

#def play_chord(chord_notes, duration=1.0):
#    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
#    wave = np.zeros_like(t)
#    
#    for note in chord_notes:
#        freq = note_to_freq(note)
#        wave += np.sin(2 * np.pi * freq * t)
#    
#    wave = wave / (len(chord_notes) + 1)
#    
#    p = pyaudio.PyAudio()
#    stream = p.open(format=pyaudio.paFloat32,
#                    channels=1,
#                    rate=SAMPLE_RATE,
#                    output=True)
#    stream.write(wave.astype(np.float32).tobytes())
#    stream.close()
#    p.terminate()

#def play_progression(progression, beats_per_chord=4):
#    for func, chord in progression:
#        notes = parse_chord(chord)
#        print(f"  {chord} ({func})", end=" ", flush=True)
#        play_chord(notes, BEAT_LENGTH * beats_per_chord)
#    print()

# ============================================
# MIDI保存
# ============================================
def save_as_midi(progression, filename="progression.mid", beats_per_chord=4):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_chord = ticks_per_beat * beats_per_chord
    
    for func, chord in progression:
        notes = parse_chord(chord)
        # parse_chordはライブラリを使用に変更する
        
        for note in notes:
            track.append(Message('note_on', note=note, velocity=80, time=0))
        for note in notes:
            track.append(Message('note_off', note=note, velocity=0, time=ticks_per_chord))
    
    mid.save(filename)
    print(f"\nMIDI保存: {filename}")

# ============================================
# メイン：生成→再生→保存
# ============================================
def main():
    generator = ChordProgressionGenerator(CONFIG)
    
    print("=== コード進行生成 ===")
    print("パターン: ttsd, ttts, tsdd, tdst などからランダム")
    print()
    
    while True:
        # 生成
        progression = generator.generate(bars=4)
        print(f"進行: {generator.pretty_print(progression)}")
        duration = [1, 1, 1, 1]
        
        # 再生
        print("再生:", end=" ")
        play_wave_sound.play_chord(progression, duration)
        #play_progression(progression)
        
        # アクション
        cmd = input("\n[r]再生成 [s]MIDI保存 [q]終了: ").lower()
        if cmd == 'q':
            break
        elif cmd == 's':
            filename = input("ファイル名 (default: progression.mid): ").strip()
            if not filename:
                filename = "progression.mid"
            if not filename.endswith('.mid'):
                filename += '.mid'
            save_as_midi(progression, filename)
        # rの場合はそのままループ??

if __name__ == "__main__":
    main()
