import numpy as np
import pyaudio
import time

SAMPLE_RATE = 44100
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_freq(note, octave=4):
    """Convert note name to frequency in Hz"""
    if isinstance(note, (int, float)):
        return note
    
    try:
        if len(note) > 1 and note[1] == '#':
            name = note[:2]
            octave = int(note[2:]) if len(note) > 2 else octave
        else:
            name = note[0]
            octave = int(note[1:]) if len(note) > 1 else octave
        
        semitones = NOTE_NAMES.index(name) - 9
        return 440.0 * (2.0 ** ((semitones + (octave - 4) * 12) / 12.0))
    except:
        return 440.0

def apply_envelope(wave, attack=0.003, release=0.003):
    """Apply attack and release envelope"""
    envelope = np.ones_like(wave)
    samples = len(wave)
    
    attack_samples = int(attack * SAMPLE_RATE)
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    release_samples = int(release * SAMPLE_RATE)
    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    
    return wave * envelope

def play_chord(chords, durations, tempo=120, style='normal', 
                          waveform='sine', volume=0.3, envelope=(0.003, 0.003)):
    """
    コード進行を正確なタイミングで再生（ストリーム開きっぱなし）
    
    Args:
        chords: コードのリスト（各要素はCHORDSのキーまたは音名リスト）
        durations: 各コードの拍数リスト
        tempo: テンポ（BPM）
        style: 'normal', 'legato', 'staccato'
        waveform: 'sine', 'square', 'sawtooth', 'triangle'
    """
    beat_duration = 60.0 / tempo
    
    # スタイルごとの音の長さの比率
    note_lengths = {
        'legato': 0.98,
        'normal': 0.95,
        'staccato': 0.60,
    }
    note_length = note_lengths.get(style, 0.95)
    
    attack, release = envelope
    
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        output=True
    )
    
    for chord, duration in zip(chords, durations):
        # コードの音名リストを取得
        if isinstance(chord, str):
            # CHORDS辞書から取得
            chord_notes = CHORDS.get(chord, [chord])  # 見つからない場合はそのまま
        else:
            chord_notes = chord
        
        chord_duration = duration * beat_duration
        play_duration = chord_duration * note_length
        silence_duration = chord_duration - play_duration
        
        # 音を鳴らす部分の波形生成
        t = np.linspace(0, play_duration, int(SAMPLE_RATE * play_duration), False)
        wave = np.zeros_like(t)
        
        for note in chord_notes:
            freq = note_to_freq(note)
            if waveform == 'sine':
                wave += np.sin(2 * np.pi * freq * t)
            elif waveform == 'square':
                wave += np.sign(np.sin(2 * np.pi * freq * t))
            elif waveform == 'sawtooth':
                wave += 2 * (t * freq % 1) - 1
            elif waveform == 'triangle':
                wave += 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        
        # 正規化
        wave = wave / len(chord_notes)
        
        # エンベロープ適用
        wave = apply_envelope(wave, attack, release)
        
        # ボリューム調整
        wave = wave * volume
        
        # クリッピング防止
        max_amp = np.max(np.abs(wave))
        if max_amp > 1.0:
            wave = wave / max_amp * 0.9
        
        # 再生
        stream.write(wave.astype(np.float32).tobytes())
        
        # 残りの時間は無音
        if silence_duration > 0.0001:
            silence = np.zeros(int(SAMPLE_RATE * silence_duration))
            stream.write(silence.astype(np.float32).tobytes())
    
    stream.close()
    p.terminate()

# メロディ再生関数
def play_melody(notes, durations, tempo=120, style='normal', 
                volume=0.3, envelope=(0.003, 0.003)):
    """
    メロディを正確なタイミングで再生
    
    style:
        'normal'   - 0.78 (標準)
        'legato'   - 0.98 (なめらか)
        'staccato' - 0.40 (短く切る)
    """
    beat_duration = 60.0 / tempo
    
    note_lengths = {
        'legato': 0.98,
        'normal': 0.78,
        'staccato': 0.40,
    }
    note_length = note_lengths.get(style, 0.78)
    
    attack, release = envelope
    
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        output=True
    )
    
    for note, duration in zip(notes, durations):
        note_duration = duration * beat_duration
        
        if note == 'rest':
            silence = np.zeros(int(SAMPLE_RATE * note_duration))
            stream.write(silence.astype(np.float32).tobytes())
            
        else:
            play_duration = note_duration * note_length
            
            # 音を鳴らす部分
            t = np.linspace(0, play_duration, int(SAMPLE_RATE * play_duration), False)
            freq = note_to_freq(note)
            wave = np.sin(2 * np.pi * freq * t)
            wave = apply_envelope(wave, attack, release)
            wave = wave * volume
            
            # クリッピング防止
            max_amp = np.max(np.abs(wave))
            if max_amp > 1.0:
                wave = wave / max_amp * 0.9
            
            stream.write(wave.astype(np.float32).tobytes())
            
            # 残りの時間は無音
            remaining = note_duration - play_duration
            if remaining > 0.0001:
                silence = np.zeros(int(SAMPLE_RATE * remaining))
                stream.write(silence.astype(np.float32).tobytes())
    
    stream.close()
    p.terminate()

# コード定義
CHORDS = {
    'C': ['C2', 'E4', 'G4', 'C4'],
    'Dm': ['D2', 'F4', 'A4', 'D4'],
    'Em': ['E2', 'G4', 'B3', 'E4'],
    'F': ['F2', 'A4', 'C4', 'F4'],
    'G': ['G2', 'B4', 'D4', 'G4'],
    'Am': ['A2', 'C4', 'E4', 'A4'],
    'Bdim': ['B2', 'D4', 'F4', 'B4'],
    'C7': ['C2', 'E4', 'G4', 'Bb4'],
    'G7': ['G2', 'B4', 'D4', 'F4'],
    'Dm7': ['D2', 'F4', 'A4', 'C4'],
}

# 使用例
if __name__ == "__main__":
    print("=== melody ===")
    melody = ['C', 'D', 'E', 'F', 'G']
    duration = [1, 1, 1, 1, 2]
    play_melody(melody, duration,tempo=120, style='normal')
    time.sleep(1)

    print("=== コード進行（ノーマル）===")
    progression = ['C', 'G', 'Am', 'F']
    duration = [2, 2, 2, 2, 2, 2, 2, 2]
    play_chord(progression, duration,tempo=120, style='normal', waveform='sine')
    time.sleep(1)
    
    print("\n=== コード進行（スタッカート）===")
    progression = ['C', 'G', 'Am', 'Em', 'F', 'C', 'Dm7', 'G7']
    duration = [1, 1, 1, 1, 1, 1, 1, 1]
    play_chord(progression, duration, tempo=150, style='staccato', waveform='sine')
    time.sleep(1)
    
    print("\n=== コード進行（レガート＋スクエア波）===")
    progression = ['C', 'Am', 'Dm', 'G7', 'C']
    duration = [2, 2, 2, 2, 4]
    play_chord(progression, duration,tempo=80, style='legato', waveform='square', volume=0.2)
