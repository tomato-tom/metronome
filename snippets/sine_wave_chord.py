import numpy as np
import pyaudio
import time

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

def play_note(note, duration=0.5, volume=0.3):
    """Play a single note with envelope to prevent clicks"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = note_to_freq(note)
    
    # Generate sine wave
    wave = np.sin(2 * np.pi * freq * t)
    
    # Apply envelope
    wave = apply_envelope(wave, attack=0.005, release=0.005)
    
    # Adjust volume
    wave = wave * volume
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True)
    stream.write(wave.astype(np.float32).tobytes())
    stream.close()
    p.terminate()

def play_chord(chord_notes, duration=1.0, fade_out=False, waveform='sine'):
    """Play a chord with optional fade out and different waveforms"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
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
    
    # Normalize
    wave = wave / len(chord_notes)
    
    # Apply fade out
    if fade_out:
        fade = np.linspace(1, 0, len(wave))
        wave *= fade
    
    # Add some harmonics for richer sound
    if waveform == 'sine':
        wave_harmonics = np.zeros_like(t)
        for note in chord_notes:
            freq = note_to_freq(note)
            wave_harmonics += np.sin(2 * np.pi * freq * t)
            wave_harmonics += 0.5 * np.sin(4 * np.pi * freq * t)  # 1st harmonic
            wave_harmonics += 0.25 * np.sin(6 * np.pi * freq * t)  # 2nd harmonic
        wave_harmonics = wave_harmonics / len(chord_notes) / 1.75
        wave = wave_harmonics
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True)
    stream.write(wave.astype(np.float32).tobytes())
    stream.close()
    p.terminate()

def play_melody(notes, durations, tempo=120):
    """Play a melody with given notes and durations"""
    beat_duration = 60.0 / tempo
    
    for note, duration in zip(notes, durations):
        if note == 'rest':
            time.sleep(duration * beat_duration)
        else:
            play_note([note], duration * beat_duration)
            #time.sleep(0.05)  # Small gap between notes

def play_progression(chords, durations, tempo=120):
    """Play a chord progression"""
    beat_duration = 60.0 / tempo
    
    for chord, duration in zip(chords, durations):
        play_chord(chord, duration * beat_duration)
        time.sleep(0.05)

# Example chord definitions
CHORDS = {
    'C': ['C2', 'C4', 'E4', 'G4'],
    'Dm': ['D2', 'D4', 'F4', 'A4'],
    'Em': ['B2', 'B3', 'E4', 'G4'],
    'F': ['F2', 'C4', 'F4', 'A4'],
    'G': ['G2', 'B3', 'D4', 'G4'],
    'Am': ['A2', 'C4', 'E4', 'A4'],
    'Bdim': ['B2', 'B3', 'D4', 'F4'],
}

# Example usage
if __name__ == "__main__":
    print("Playing C major chord...")
    #play_chord(CHORDS['C'], duration=2.0, fade_out=True, waveform='sawtooth')
    
    time.sleep(0.5)
    
    print("Playing simple melody...")
    melody_notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5',
                    'B4', 'A4', 'G4', 'F4', 'E4', 'D4', 'C4']
    melody_durations = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
                        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]
    play_melody(melody_notes, melody_durations, tempo=120)
    
    time.sleep(1)
    
    print("Playing chord progression...")
    #progression = [CHORDS['C'], CHORDS['G'], CHORDS['Am'], CHORDS['F']]
    progression = [CHORDS['C'], CHORDS['Dm'], CHORDS['G'], CHORDS['Em'],
                   CHORDS['Am'], CHORDS['F'], CHORDS['C'], CHORDS['G']]
    prog_durations = [2, 2, 2, 2,
                      2, 2, 2, 2]
    #play_progression(progression, prog_durations, tempo=100)

