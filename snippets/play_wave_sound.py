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

def generate_waveform(notes, duration, waveform='sine', sample_rate=SAMPLE_RATE):
    """
    1つまたは複数の音の波形を生成
    
    Args:
        notes: 単一の音名（str）または音名のリスト
        duration: 再生時間（秒）
        waveform: 'sine', 'square', 'sawtooth', 'triangle'
    
    Returns:
        wave: 生成された波形（正規化前）
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 単一の音の場合
    if isinstance(notes, str):
        freq = note_to_freq(notes)
        if waveform == 'sine':
            return np.sin(2 * np.pi * freq * t)
        elif waveform == 'square':
            return np.sign(np.sin(2 * np.pi * freq * t))
        elif waveform == 'sawtooth':
            return 2 * (t * freq % 1) - 1
        elif waveform == 'triangle':
            return 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    
    # 複数の音（コード）の場合
    else:
        wave = np.zeros_like(t)
        for note in notes:
            freq = note_to_freq(note)
            if waveform == 'sine':
                wave += np.sin(2 * np.pi * freq * t)
            elif waveform == 'square':
                wave += np.sign(np.sin(2 * np.pi * freq * t))
            elif waveform == 'sawtooth':
                wave += 2 * (t * freq % 1) - 1
            elif waveform == 'triangle':
                wave += 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        return wave

def play_audio(wave, stream=None, volume=0.3, envelope=(0.003, 0.003)):
    """
    波形にエンベロープ適用、音量調整、正規化して再生
    
    Args:
        wave: 生波形
        stream: PyAudioストリーム（Noneなら新規作成）
        volume: 音量
        envelope: (attack, release) 秒
    
    Returns:
        stream: 使用したストリーム（既存の場合はそのまま）
    """
    # エンベロープ適用
    attack, release = envelope
    wave = apply_envelope(wave, attack, release)
    
    # 音量調整
    wave = wave * volume
    
    # クリッピング防止
    max_amp = np.max(np.abs(wave))
    if max_amp > 1.0:
        wave = wave / max_amp * 0.9
    
    # 再生
    need_cleanup = False
    if stream is None:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                       channels=1,
                       rate=SAMPLE_RATE,
                       output=True)
        need_cleanup = True
    
    stream.write(wave.astype(np.float32).tobytes())
    
    if need_cleanup:
        stream.close()
        p.terminate()
        return None
    return stream

def play_silence(duration, stream):
    """無音を再生"""
    if duration > 0.0001:
        samples = int(SAMPLE_RATE * duration)
        stream.write(np.zeros(samples).astype(np.float32).tobytes())

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
    コード進行を再生
    
    Args:
        chords: コードのリスト（各要素はCHORDSのキーまたは音名リスト）
        durations: 各コードの拍数リスト
        tempo: テンポ（BPM）
        style: 'normal', 'legato', 'staccato'
        waveform: 'sine', 'square', 'sawtooth', 'triangle'
    """
    beat_duration = 60.0 / tempo
    note_lengths = {'legato': 0.98, 'normal': 0.95, 'staccato': 0.60}
    note_length = note_lengths.get(style, 0.95)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                   channels=1,
                   rate=SAMPLE_RATE,
                   output=True)
    
    for chord, duration in zip(chords, durations):
        chord_duration = duration * beat_duration
        play_duration = chord_duration * note_length
        silence_duration = chord_duration - play_duration
        
        # コードの音名リストを取得
        notes = CHORDS[chord] if isinstance(chord, str) else chord
        
        # 波形生成（共通関数）
        wave = generate_waveform(notes, play_duration, waveform)
        
        # 再生（ストリーム再利用）
        play_audio(wave, stream, volume, envelope)
        
        # 無音
        play_silence(silence_duration, stream)
    
    stream.close()
    p.terminate()

def play_melody(notes, durations, tempo=120, style='normal', 
                waveform='sine', volume=0.3, envelope=(0.003, 0.003)):
    """
    メロディを再生
    
    Args:
        notes: List of notes
        durations: List of each notes
        tempo: tempo（BPM）
        style: 'normal', 'legato', 'staccato'
        waveform: 'sine', 'square', 'sawtooth', 'triangle'
    """
    beat_duration = 60.0 / tempo
    note_lengths = {'legato': 0.98, 'normal': 0.78, 'staccato': 0.40}
    note_length = note_lengths.get(style, 0.78)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                   channels=1,
                   rate=SAMPLE_RATE,
                   output=True)
    
    for note, duration in zip(notes, durations):
        note_duration = duration * beat_duration
        
        if note == 'rest':
            play_silence(note_duration, stream)
        else:
            play_duration = note_duration * note_length
            silence_duration = note_duration - play_duration
            
            # 波形生成（共通関数）
            wave = generate_waveform(note, play_duration, 'sine')  # メロディは常にsine
            
            # 再生（ストリーム再利用）
            play_audio(wave, stream, volume, envelope)
            
            # 無音
            play_silence(silence_duration, stream)
    
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
    play_melody(melody, duration,tempo=180, style='normal')
    time.sleep(1)

    print("=== コード進行（ノーマル）===")
    progression = ['C', 'G', 'Am', 'F', 'C']
    duration = [2, 2, 2, 2, 4]
    play_chord(progression, duration,tempo=120, style='normal', waveform='sine')
    time.sleep(1)
    
    print("\n=== コード進行（スタッカート）===")
    progression = ['C', 'G', 'Am', 'Em', 'F', 'C', 'Dm7', 'G7']
    duration = [1, 1, 1, 1, 1, 1, 1, 1]
    play_chord(progression, duration, tempo=150, style='staccato', waveform='sine')
    progression = ['C']
    duration = [2]
    play_chord(progression, duration,tempo=150, style='normal', waveform='sine')
    time.sleep(1)
    
    print("\n=== コード進行（レガート＋スクエア波）===")
    progression = ['C', 'Am', 'Dm', 'G7', 'C']
    duration = [2, 2, 2, 2, 4]
    play_chord(progression, duration,tempo=80, style='legato', waveform='square', volume=0.2)
