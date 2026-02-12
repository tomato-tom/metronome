import numpy as np
import pyaudio
import time
from time import sleep

SAMPLE_RATE = 44100
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def note_to_freq(note, octave=4):
    """Convert note name to frequency in Hz"""
    if isinstance(note, (int, float)):
        return note  # Already a frequency
    
    # Handle note format like 'C4', 'A#5', etc.
    if len(note) > 1:
        if note[1] == '#':
            name = note[:2]
            octave = int(note[2:]) if len(note) > 2 else octave
        else:
            name = note[0]
            octave = int(note[1:]) if len(note) > 1 else octave
    else:
        name = note[0]
        octave = int(note[1:]) if len(note) > 1 else octave
    
    # A4 = 440Hz
    semitones = NOTE_NAMES.index(name) - 9  # A is index 9
    return 440.0 * (2.0 ** ((semitones + (octave - 4) * 12) / 12.0))

def apply_envelope(wave, attack=0.01, release=0.01):
    """Apply attack and release envelope to prevent clicking"""
    envelope = np.ones_like(wave)
    samples = len(wave)
    
    # Attack (fade in)
    attack_samples = int(attack * SAMPLE_RATE)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Release (fade out)
    release_samples = int(release * SAMPLE_RATE)
    envelope[-release_samples:] = np.linspace(1, 0, release_samples)
    
    return wave * envelope

def play_melody(notes, durations, tempo=120, style='normal', callback=None):
    """
    style:
        'normal'
        'legato'
        'staccato'
    callback: 各ノート再生前に呼ばれる関数（タイムスタンプ付き）
    """
    beat_duration = 60.0 / tempo
    
    if style == 'legato':
        note_length = 0.98
    elif style == 'normal':
        note_length = 0.78
    elif style == 'staccato':
        note_length = 0.4
    
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLE_RATE,
        output=True
    )
    
    for note, duration in zip(notes, durations):
        note_duration = duration * beat_duration
        
        if callback:
            callback(note, time.time())
        
        if note == 'rest':
            silence = np.zeros(int(SAMPLE_RATE * note_duration))
            stream.write(silence.astype(np.float32).tobytes())
            
        else:
            # 音符は指定された長さだけ音を鳴らし、残りは無音
            play_duration = note_duration * note_length
            
            # 音を鳴らす部分
            t = np.linspace(0, play_duration, int(SAMPLE_RATE * play_duration), False)
            freq = note_to_freq(note)
            wave = np.sin(2 * np.pi * freq * t)
            wave = apply_envelope(wave, 0.003, 0.003)
            wave = wave * 0.3
            stream.write(wave.astype(np.float32).tobytes())
            
            # 残りの時間は無音（休符と同じ処理）
            remaining = note_duration - play_duration
            if remaining > 0:
                silence = np.zeros(int(SAMPLE_RATE * remaining))
                stream.write(silence.astype(np.float32).tobytes())
    
    stream.close()
    p.terminate()

# Example usage

if __name__ == "__main__":
    # style:
    # - normal
    # - staccato
    # - legato

    style = 'normal'
    print(f'--- Playing melody with {style} -------')
    notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
    durations = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]
    play_melody(notes, durations, tempo=128, style=style)
    sleep(1)

    style = 'staccato'
    print(f'--- Playing melody with {style} -------')
    notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
    durations = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]
    play_melody(notes, durations, tempo=128, style=style)
    sleep(1)

    style = 'legato'
    print(f'--- Playing melody with {style} -------')
    notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
    durations = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]
    play_melody(notes, durations, tempo=128, style=style)

