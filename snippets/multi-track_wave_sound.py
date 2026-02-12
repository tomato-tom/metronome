"""
Multi-track Wave Sound Generator
--------------------------------
A Python module for generating and playing multi-track audio with support for melodies,
chords, and various waveforms. Includes audio playback and WAV file export functionality.
"""

import numpy as np
import pyaudio
import time

# ====================================================
# Global Constants
# ====================================================
SAMPLE_RATE = 44100  # CD quality sample rate (Hz)
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


# ====================================================
# Note Utilities Class
# ====================================================
class NoteUtils:
    """Utility class for note and chord operations."""
    
    @staticmethod
    def note_to_freq(note, octave=4):
        """
        Convert note name to frequency in Hz.
        
        Args:
            note: Note name (e.g., 'C4', 'F#5') or numeric frequency
            octave: Default octave if not specified in note string
        
        Returns:
            Frequency in Hz
        """
        # If numeric value is provided, assume it's already frequency
        if isinstance(note, (int, float)):
            return note
        
        try:
            # Extract note name and octave
            if len(note) > 1 and note[1] == '#':
                name = note[:2]  # Sharp note (C#, F#, etc.)
                octave = int(note[2:]) if len(note) > 2 else octave
            else:
                name = note[0]  # Natural note
                octave = int(note[1:]) if len(note) > 1 else octave
            
            # Calculate frequency: A4 = 440Hz
            semitones = NOTE_NAMES.index(name) - 9
            return 440.0 * (2.0 ** ((semitones + (octave - 4) * 12) / 12.0))
        except (ValueError, IndexError):
            # Fallback to A4 if parsing fails
            return 440.0
    
    @staticmethod
    def apply_envelope(wave, attack=0.003, release=0.003, sample_rate=SAMPLE_RATE):
        """
        Apply ADSR-like envelope to waveform.
        
        Args:
            wave: Input waveform array
            attack: Attack time in seconds
            release: Release time in seconds
            sample_rate: Audio sample rate
        
        Returns:
            Waveform with envelope applied
        """
        envelope = np.ones_like(wave)
        samples = len(wave)
        
        # Attack phase (fade in)
        attack_samples = int(attack * sample_rate)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Release phase (fade out)
        release_samples = int(release * sample_rate)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)
        
        return wave * envelope
    
    @staticmethod
    def generate_waveform(notes, duration, waveform='sine', sample_rate=SAMPLE_RATE):
        """
        Generate waveform for single note or chord.
        
        Args:
            notes: Single note string or list of note strings
            duration: Duration in seconds
            waveform: Waveform type ('sine', 'square', 'sawtooth', 'triangle')
            sample_rate: Audio sample rate
        
        Returns:
            Generated waveform array
        """
        # Create time array
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Single note case
        if isinstance(notes, str):
            freq = NoteUtils.note_to_freq(notes)
            return NoteUtils._generate_single_note(t, freq, waveform)
        
        # Multiple notes (chord) case
        else:
            wave = np.zeros_like(t)
            for note in notes:
                freq = NoteUtils.note_to_freq(note)
                wave += NoteUtils._generate_single_note(t, freq, waveform)
            return wave
    
    @staticmethod
    def _generate_single_note(t, freq, waveform):
        """Generate single frequency waveform."""
        if waveform == 'sine':
            return np.sin(2 * np.pi * freq * t)
        elif waveform == 'square':
            return np.sign(np.sin(2 * np.pi * freq * t))
        elif waveform == 'sawtooth':
            return 2 * (t * freq % 1) - 1
        elif waveform == 'triangle':
            return 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        else:
            return np.sin(2 * np.pi * freq * t)  # Default to sine
    
    @classmethod
    def parse_chord_symbol(cls, chord_symbol):
        """
        Parse chord symbol and return root note and interval list.
        
        Supported chord types:
            Major: 'C', 'CM'
            Minor: 'Cm'
            Diminished: 'Cdim'
            Augmented: 'Caug'
            Seventh: 'C7'
            Minor seventh: 'Cm7'
            Major seventh: 'CM7', 'Cmaj7'
            Half-diminished: 'Cm7b5'
            Diminished seventh: 'Cdim7'
            Sixth: 'C6'
            Minor sixth: 'Cm6'
            Suspended fourth: 'Csus4'
            Seventh suspended fourth: 'C7sus4'
            Ninth: 'C9'
        
        Args:
            chord_symbol: Chord symbol string
        
        Returns:
            Tuple of (root_note, intervals_list)
        """
        # Extract root note
        if len(chord_symbol) > 1 and chord_symbol[1] == '#':
            root = chord_symbol[:2]
            suffix = chord_symbol[2:]
        else:
            root = chord_symbol[0]
            suffix = chord_symbol[1:]
        
        # Define intervals for different chord types (semitones from root)
        chord_intervals = {
            '': [0, 4, 7],              # Major
            'M': [0, 4, 7],             # Major
            'm': [0, 3, 7],             # Minor
            'dim': [0, 3, 6],           # Diminished
            'aug': [0, 4, 8],           # Augmented
            '7': [0, 4, 7, 10],         # Dominant 7th
            'm7': [0, 3, 7, 10],        # Minor 7th
            'M7': [0, 4, 7, 11],        # Major 7th
            'maj7': [0, 4, 7, 11],      # Major 7th
            'm7b5': [0, 3, 6, 10],      # Half-diminished
            'dim7': [0, 3, 6, 9],       # Diminished 7th
            '6': [0, 4, 7, 9],          # 6th
            'm6': [0, 3, 7, 9],         # Minor 6th
            'sus4': [0, 5, 7],          # Suspended 4th
            '7sus4': [0, 5, 7, 10],     # 7th suspended 4th
            '9': [0, 4, 7, 10, 14],     # 9th
        }
        
        # Get intervals or default to major
        intervals = chord_intervals.get(suffix, [0, 4, 7])
        
        return root, intervals
    
    @classmethod
    def build_chord(cls, chord_symbol, bass_octave=2, chord_octave=4, intervals=None):
        """
        Build chord notes from chord symbol and intervals.
        
        Args:
            chord_symbol: Chord symbol (e.g., 'C', 'Am', 'D7')
            bass_octave: Octave for bass note (default: 2)
            chord_octave: Base octave for chord notes (default: 4)
            intervals: Optional pre-parsed intervals list
        
        Returns:
            List of note strings
        """
        # Parse chord if intervals not provided
        if intervals is None:
            root, intervals = cls.parse_chord_symbol(chord_symbol)
        else:
            # Extract root only
            if len(chord_symbol) > 1 and chord_symbol[1] == '#':
                root = chord_symbol[:2]
            else:
                root = chord_symbol[0]
        
        # Get root note index
        if len(root) > 1 and root[1] == '#':
            root_index = NOTE_NAMES.index(root[:2])
        else:
            root_index = NOTE_NAMES.index(root[0])
        
        chord_notes = []
        
        # Add bass note (root in lower octave)
        chord_notes.append(f"{root}{bass_octave}")
        
        # Add chord notes with intervals
        for interval in intervals:
            note_index = (root_index + interval) % 12
            note_name = NOTE_NAMES[note_index]
            
            # Calculate appropriate octave
            octave = chord_octave + ((root_index + interval) // 12)
            chord_notes.append(f"{note_name}{octave}")
        
        return chord_notes


# ====================================================
# Audio Player Class
# ====================================================
class AudioPlayer:
    """Audio playback handler using PyAudio."""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        """
        Initialize audio player.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.p = None
        self.stream = None
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures resources are freed."""
        self.close()
    
    def open(self):
        """Open audio stream."""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,  # Mono
            rate=self.sample_rate,
            output=True
        )
        return self
    
    def close(self):
        """Close audio stream and release resources."""
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.p:
            self.p.terminate()
            self.p = None
    
    def play_wave(self, wave, volume=0.3, envelope=(0.003, 0.003)):
        """
        Play waveform through audio output.
        
        Args:
            wave: Waveform array
            volume: Volume scaling factor (0.0-1.0)
            envelope: Tuple of (attack, release) times in seconds
        """
        # Apply attack/release envelope
        attack, release = envelope
        wave = NoteUtils.apply_envelope(wave, attack, release, self.sample_rate)
        
        # Apply volume
        wave = wave * volume
        
        # Prevent clipping
        max_amp = np.max(np.abs(wave))
        if max_amp > 1.0:
            wave = wave / max_amp * 0.9
        
        # Play audio
        if self.stream is None:
            self.open()
        self.stream.write(wave.astype(np.float32).tobytes())
        return self
    
    def play_silence(self, duration):
        """
        Play silence (pause) for specified duration.
        
        Args:
            duration: Silence duration in seconds
        """
        if duration > 0.0001:  # Skip negligible durations
            samples = int(self.sample_rate * duration)
            silence = np.zeros(samples)
            self.stream.write(silence.astype(np.float32).tobytes())
        return self


# ====================================================
# Abstract Track Class
# ====================================================
class Track:
    """Abstract base class for audio tracks."""
    
    def __init__(self, tempo=120, style='normal', volume=0.2):
        """
        Initialize track.
        
        Args:
            tempo: Beats per minute
            style: Playing style ('legato', 'normal', 'staccato')
            volume: Volume level (0.0-1.0)
        """
        self.tempo = tempo
        self.style = style
        self.volume = volume
        self.beat_duration = 60.0 / tempo  # Duration of one beat in seconds
    
    def render(self, total_duration, sample_rate=SAMPLE_RATE):
        """
        Render track waveform.
        
        Args:
            total_duration: Total duration to render
            sample_rate: Audio sample rate
        
        Returns:
            Rendered waveform array
        """
        raise NotImplementedError("Subclasses must implement render()")
    
    def _get_note_length(self, style_dict):
        """
        Get note length factor based on style.
        
        Args:
            style_dict: Dictionary mapping style names to note length factors
        
        Returns:
            Note length factor (1.0 = full duration)
        """
        return style_dict.get(self.style, list(style_dict.values())[0])


# ====================================================
# Melody Track Class
# ====================================================
class MelodyTrack(Track):
    """Track for melody (single notes) playback."""
    
    # Note length factors for different playing styles
    NOTE_LENGTHS = {
        'legato': 0.98,    # Almost full duration, connected notes
        'normal': 0.78,    # Standard duration, slight separation
        'staccato': 0.40   # Short, detached notes
    }
    
    def __init__(self, notes, durations, tempo=120, style='normal', 
                 volume=0.2, waveform='sine'):
        """
        Initialize melody track.
        
        Args:
            notes: List of note strings or frequencies
            durations: List of note durations in beats
            tempo: Beats per minute
            style: Playing style
            volume: Volume level
            waveform: Waveform type
        """
        super().__init__(tempo, style, volume)
        self.notes = notes
        self.durations = durations
        self.waveform = waveform
    
    def render(self, total_duration=None, sample_rate=SAMPLE_RATE):
        """
        Render melody waveform.
        
        Args:
            total_duration: Total duration to render
            sample_rate: Audio sample rate
        
        Returns:
            Rendered waveform array
        """
        # Calculate total track duration
        track_duration = sum(d * self.beat_duration for d in self.durations)
        if total_duration is None:
            total_duration = track_duration
        
        # Initialize waveform array
        t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
        wave = np.zeros_like(t)
        
        # Get note length factor based on style
        note_length = self._get_note_length(self.NOTE_LENGTHS)
        current_time = 0
        
        # Generate each note
        for note, duration in zip(self.notes, self.durations):
            note_duration = duration * self.beat_duration
            
            if note != 'rest':
                play_duration = note_duration * note_length
                
                # Calculate sample indices
                start_idx = int(round(current_time * sample_rate))
                end_idx = int(round((current_time + play_duration) * sample_rate))
                
                # Generate note waveform if within bounds
                if start_idx < len(wave) and end_idx > start_idx:
                    wave_note = NoteUtils.generate_waveform(
                        note, 
                        play_duration, 
                        self.waveform, 
                        sample_rate
                    )
                    
                    # Adjust length to fit exactly
                    target_len = end_idx - start_idx
                    if len(wave_note) > target_len:
                        wave_note = wave_note[:target_len]
                    elif len(wave_note) < target_len:
                        wave_note = np.pad(wave_note, (0, target_len - len(wave_note)), 'constant')
                    
                    # Add to waveform with volume scaling
                    wave[start_idx:end_idx] += wave_note * self.volume
            # Rest: no sound generated
            
            current_time += note_duration
        
        return wave


# ====================================================
# Chord Track Class
# ====================================================
class ChordTrack(Track):
    """Track for chord progression playback."""
    
    # Note length factors for different playing styles
    NOTE_LENGTHS = {
        'legato': 0.98,    # Connected chords
        'normal': 0.95,    # Standard chord duration
        'staccato': 0.60   # Short, detached chords
    }
    
    def __init__(self, chords, durations, tempo=120, style='normal', 
                 volume=0.15, waveform='sine'):
        """
        Initialize chord track.
        
        Args:
            chords: List of chord symbols or note lists
            durations: List of chord durations in beats
            tempo: Beats per minute
            style: Playing style
            volume: Volume level
            waveform: Waveform type
        """
        super().__init__(tempo, style, volume)
        self.chords = chords
        self.durations = durations
        self.waveform = waveform
    
    def render(self, total_duration=None, sample_rate=SAMPLE_RATE):
        """
        Render chord waveform.
        
        Args:
            total_duration: Total duration to render
            sample_rate: Audio sample rate
        
        Returns:
            Rendered waveform array
        """
        # Calculate total track duration
        track_duration = sum(d * self.beat_duration for d in self.durations)
        if total_duration is None:
            total_duration = track_duration
        
        # Initialize waveform array
        t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
        wave = np.zeros_like(t)
        
        # Get note length factor based on style
        note_length = self._get_note_length(self.NOTE_LENGTHS)
        current_time = 0
        
        # Generate each chord
        for chord, duration in zip(self.chords, self.durations):
            chord_duration = duration * self.beat_duration
            play_duration = chord_duration * note_length
            
            # Calculate sample indices
            start_idx = int(round(current_time * sample_rate))
            end_idx = int(round((current_time + play_duration) * sample_rate))
            
            # Generate chord waveform if within bounds
            if start_idx < len(wave) and end_idx > start_idx:
                # Convert chord symbol to note list if necessary
                if isinstance(chord, str):
                    notes = NoteUtils.build_chord(chord)
                else:
                    notes = chord
                
                # Generate chord waveform
                wave_chord = NoteUtils.generate_waveform(
                    notes,
                    play_duration,
                    self.waveform,
                    sample_rate
                )
                
                # Normalize by number of notes to prevent clipping
                wave_chord = wave_chord / len(notes)
                
                # Adjust length to fit exactly
                target_len = end_idx - start_idx
                if len(wave_chord) > target_len:
                    wave_chord = wave_chord[:target_len]
                elif len(wave_chord) < target_len:
                    wave_chord = np.pad(wave_chord, (0, target_len - len(wave_chord)), 'constant')
                
                # Add to waveform with volume scaling
                wave[start_idx:end_idx] += wave_chord * self.volume
            
            current_time += chord_duration
        
        return wave


# ====================================================
# Song Class
# ====================================================
class Song:
    """Main song class that manages multiple tracks and mixing."""
    
    def __init__(self, tempo=120):
        """
        Initialize song.
        
        Args:
            tempo: Global tempo in beats per minute
        """
        self.tempo = tempo
        self.tracks = []
    
    def add_track(self, track):
        """
        Add pre-configured track to song.
        
        Args:
            track: Track object
        
        Returns:
            Self for method chaining
        """
        self.tracks.append(track)
        return self
    
    def add_melody(self, notes, durations, style='normal', volume=0.2, waveform='sine'):
        """
        Add melody track to song.
        
        Args:
            notes: List of note strings or frequencies
            durations: List of note durations in beats
            style: Playing style
            volume: Volume level
            waveform: Waveform type
        
        Returns:
            Self for method chaining
        """
        track = MelodyTrack(notes, durations, self.tempo, style, volume, waveform)
        self.tracks.append(track)
        return self
    
    def add_chords(self, chords, durations, style='normal', volume=0.15, waveform='sine'):
        """
        Add chord track to song.
        
        Args:
            chords: List of chord symbols or note lists
            durations: List of chord durations in beats
            style: Playing style
            volume: Volume level
            waveform: Waveform type
        
        Returns:
            Self for method chaining
        """
        track = ChordTrack(chords, durations, self.tempo, style, volume, waveform)
        self.tracks.append(track)
        return self
    
    def render(self, sample_rate=SAMPLE_RATE):
        """
        Render all tracks and mix into single waveform.
        
        Args:
            sample_rate: Audio sample rate
        
        Returns:
            Mixed waveform array
        """
        if not self.tracks:
            return np.array([])
        
        # Calculate total duration (use longest track)
        total_duration = 0
        for track in self.tracks:
            track_duration = sum(d * (60.0 / track.tempo) for d in track.durations)
            total_duration = max(total_duration, track_duration)
        
        # Initialize mixed waveform
        t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
        wave_total = np.zeros_like(t)
        
        # Render and mix all tracks
        for track in self.tracks:
            wave_track = track.render(total_duration, sample_rate)
            wave_total += wave_track
        
        # Normalize to prevent clipping
        max_amp = np.max(np.abs(wave_total))
        if max_amp > 1.0:
            wave_total = wave_total / max_amp * 0.9
        
        return wave_total
    
    def play(self, sample_rate=SAMPLE_RATE):
        """
        Play the rendered song through audio output.
        
        Args:
            sample_rate: Audio sample rate
        
        Returns:
            Self for method chaining
        """
        wave = self.render(sample_rate)
        
        with AudioPlayer(sample_rate) as player:
            player.play_wave(wave, volume=1.0, envelope=(0, 0))
        
        return self
    
    def save(self, filename, sample_rate=SAMPLE_RATE):
        """
        Save rendered song to WAV file.
        
        Args:
            filename: Output filename
            sample_rate: Audio sample rate
        
        Returns:
            Self for method chaining
        """
        from scipy.io import wavfile
        
        wave = self.render(sample_rate)
        # Convert to 16-bit integer format for WAV
        wave_int16 = (wave * 32767).astype(np.int16)
        wavfile.write(filename, sample_rate, wave_int16)
        print(f"✅ Saved to {filename}")
        return self


# ====================================================
# Example Usage
# ====================================================
if __name__ == "__main__":
    print("🎵 Multi-track Wave Sound Generator")
    print("===================================")
    
    # Mary Had a Little Lamb - Melody
    # Note: Format is "note_name" + "octave" (e.g., 'E5', 'D5', 'C5')
    melody = [
        'E5', 'D5', 'C5', 'D5',
        'E5', 'E5', 'E5', 'rest',
        'D5', 'D5', 'D5',
        'E5', 'G5', 'G5',
        'E5', 'D5', 'C5', 'D5',
        'E5', 'E5', 'E5', 'rest',
        'D5', 'D5', 'E5', 'D5',
        'C5'
    ]
    
    # Rhythm pattern for melody (in beats)
    melody_rhythm = [
        0.75, 0.25, 0.5, 0.5,
        0.5, 0.5, 0.5, 0.5,
        0.5, 0.5, 1.0,
        0.5, 0.5, 1.0,
        0.75, 0.25, 0.5, 0.5,
        0.5, 0.5, 0.5, 0.5,
        0.5, 0.5, 0.5, 0.5,
        1.0
    ]
    
    # Chord progression (simple I-V-I in C major)
    chords = ['C', 'C', 'G', 'C', 'C', 'C', 'G', 'C']
    chord_rhythm = [2, 2, 2, 2, 2, 2, 2, 2]  # 2 beats per chord
    
    # Uncomment examples below to try different combinations
    
    # Example 1: Melody only
    # print("\n1. Playing melody only...")
    # Song(tempo=120)\
    #     .add_melody(melody, melody_rhythm, style='normal', volume=0.2)\
    #     .play()
    
    # time.sleep(1)
    
    # Example 2: Chords only
    # print("\n2. Playing chords only...")
    # Song(tempo=120)\
    #     .add_chords(chords, chord_rhythm, style='normal', volume=0.15)\
    #     .play()
    
    # time.sleep(1)
    
    # Example 3: Melody + Chords (full arrangement)
    print("\n3. Playing melody + chords together...")
    Song(tempo=120)\
        .add_melody(melody, melody_rhythm, style='normal', volume=0.2, waveform='sine')\
        .add_chords(chords, chord_rhythm, style='normal', volume=0.15, waveform='sine')\
        .play()
    
    # Example 4: Different style combination
    # time.sleep(1)
    # print("\n4. Playing melody (normal) + chords (staccato)...")
    # Song(tempo=120)\
    #     .add_melody(melody, melody_rhythm, style='normal', volume=0.2)\
    #     .add_chords(chords, chord_rhythm, style='staccato', volume=0.15)\
    #     .play()
    
    # Example 5: Save to WAV file
    # print("\n5. Saving to WAV file...")
    # Song(tempo=120)\
    #     .add_melody(melody, melody_rhythm, style='normal')\
    #     .add_chords(chords, chord_rhythm, style='normal')\
    #     .save('mary_had_a_lamb.wav')
