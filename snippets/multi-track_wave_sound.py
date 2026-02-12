import numpy as np
import pyaudio
import time

SAMPLE_RATE = 44100
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# コード定義
CHORDS = {
    'C': ['C2', 'E4', 'G4', 'C5'],
    'Dm': ['D2', 'F4', 'A4', 'D5'],
    'Em': ['E2', 'G4', 'B4', 'E5'],
    'F': ['F2', 'A4', 'C5', 'F5'],
    'G': ['G2', 'B4', 'D5', 'G5'],
    'Am': ['A2', 'C5', 'E5', 'A5'],
    'Bdim': ['B2', 'D5', 'F5', 'B5'],
    'C7': ['C2', 'E4', 'G4', 'Bb4'],
    'G7': ['G2', 'B4', 'D5', 'F5'],
}

class NoteUtils:
    """音関連のユーティリティクラス"""
    
    @staticmethod
    def note_to_freq(note, octave=4):
        """音名を周波数に変換"""
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
    
    @staticmethod
    def apply_envelope(wave, attack=0.003, release=0.003, sample_rate=SAMPLE_RATE):
        """エンベロープ適用"""
        envelope = np.ones_like(wave)
        samples = len(wave)
        
        attack_samples = int(attack * sample_rate)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        release_samples = int(release * sample_rate)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(1, 0, release_samples)
        
        return wave * envelope
    
    @staticmethod
    def generate_waveform(notes, duration, waveform='sine', sample_rate=SAMPLE_RATE):
        """波形生成"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        if isinstance(notes, str):
            freq = NoteUtils.note_to_freq(notes)
            if waveform == 'sine':
                return np.sin(2 * np.pi * freq * t)
            elif waveform == 'square':
                return np.sign(np.sin(2 * np.pi * freq * t))
            elif waveform == 'sawtooth':
                return 2 * (t * freq % 1) - 1
            elif waveform == 'triangle':
                return 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        else:
            wave = np.zeros_like(t)
            for note in notes:
                freq = NoteUtils.note_to_freq(note)
                if waveform == 'sine':
                    wave += np.sin(2 * np.pi * freq * t)
                elif waveform == 'square':
                    wave += np.sign(np.sin(2 * np.pi * freq * t))
                elif waveform == 'sawtooth':
                    wave += 2 * (t * freq % 1) - 1
                elif waveform == 'triangle':
                    wave += 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
            return wave


class AudioPlayer:
    """オーディオ再生クラス"""
    
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.p = None
        self.stream = None
    
    def __enter__(self):
        """コンテキストマネージャ対応"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャ対応"""
        self.close()
    
    def open(self):
        """ストリームを開く"""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            output=True
        )
        return self
    
    def close(self):
        """ストリームを閉じる"""
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.p:
            self.p.terminate()
            self.p = None
    
    def play_wave(self, wave, volume=0.3, envelope=(0.003, 0.003)):
        """波形を再生"""
        # エンベロープ適用
        attack, release = envelope
        wave = NoteUtils.apply_envelope(wave, attack, release, self.sample_rate)
        
        # 音量調整
        wave = wave * volume
        
        # クリッピング防止
        max_amp = np.max(np.abs(wave))
        if max_amp > 1.0:
            wave = wave / max_amp * 0.9
        
        # 再生
        if self.stream is None:
            self.open()
        self.stream.write(wave.astype(np.float32).tobytes())
        return self
    
    def play_silence(self, duration):
        """無音を再生"""
        if duration > 0.0001:
            samples = int(self.sample_rate * duration)
            silence = np.zeros(samples)
            self.stream.write(silence.astype(np.float32).tobytes())
        return self


class Track:
    """抽象トラッククラス"""
    
    def __init__(self, tempo=120, style='normal', volume=0.2):
        self.tempo = tempo
        self.style = style
        self.volume = volume
        self.beat_duration = 60.0 / tempo
    
    def render(self, total_duration, sample_rate=SAMPLE_RATE):
        """波形をレンダリング（サブクラスで実装）"""
        raise NotImplementedError
    
    def _get_note_length(self, style_dict):
        """スタイルに応じた音の長さを取得"""
        return style_dict.get(self.style, list(style_dict.values())[0])


class MelodyTrack(Track):
    """メロディトラック"""
    
    NOTE_LENGTHS = {
        'legato': 0.98,
        'normal': 0.78,
        'staccato': 0.40
    }
    
    def __init__(self, notes, durations, tempo=120, style='normal', volume=0.2, waveform='sine'):
        super().__init__(tempo, style, volume)
        self.notes = notes
        self.durations = durations
        self.waveform = waveform
    
    def render(self, total_duration=None, sample_rate=SAMPLE_RATE):
        """メロディ波形をレンダリング"""
        # 全体の長さを計算
        track_duration = sum(d * self.beat_duration for d in self.durations)
        if total_duration is None:
            total_duration = track_duration
        
        # 時間軸
        t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
        wave = np.zeros_like(t)
        
        note_length = self._get_note_length(self.NOTE_LENGTHS)
        current_time = 0
        
        for note, duration in zip(self.notes, self.durations):
            note_duration = duration * self.beat_duration
            
            if note != 'rest':
                play_duration = note_duration * note_length
                
                # ★ 修正: round()で安全に
                start_idx = int(round(current_time * sample_rate))
                end_idx = int(round((current_time + play_duration) * sample_rate))
                
                if start_idx < len(wave) and end_idx > start_idx:
                    # ✅ generate_waveformを使用！
                    wave_note = NoteUtils.generate_waveform(
                        note, 
                        play_duration, 
                        self.waveform, 
                        sample_rate
                    )
                    
                    # 長さを調整
                    target_len = end_idx - start_idx
                    if len(wave_note) > target_len:
                        wave_note = wave_note[:target_len]
                    elif len(wave_note) < target_len:
                        wave_note = np.pad(wave_note, (0, target_len - len(wave_note)), 'constant')
                    
                    wave[start_idx:end_idx] += wave_note * self.volume
            
            current_time += note_duration
        
        return wave


class ChordTrack(Track):
    """コードトラック"""
    
    # スタイルごとの音の長さ
    NOTE_LENGTHS = {
        'legato': 0.98,
        'normal': 0.95,
        'staccato': 0.60
    }
    
    def __init__(self, chords, durations, tempo=120, style='normal', 
                 volume=0.15, waveform='sine'):
        super().__init__(tempo, style, volume)
        self.chords = chords
        self.durations = durations
        self.waveform = waveform
    
    def render(self, total_duration=None, sample_rate=SAMPLE_RATE):
        """コード波形をレンダリング"""
        # 全体の長さを計算
        track_duration = sum(d * self.beat_duration for d in self.durations)
        if total_duration is None:
            total_duration = track_duration
        
        # 時間軸
        t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
        wave = np.zeros_like(t)
        
        note_length = self._get_note_length(self.NOTE_LENGTHS)
        current_time = 0
        
        for chord, duration in zip(self.chords, self.durations):
            chord_duration = duration * self.beat_duration
            play_duration = chord_duration * note_length
            
            start_idx = int(round(current_time * sample_rate))
            end_idx = int(round((current_time + play_duration) * sample_rate))
            
            if start_idx < len(wave) and end_idx > start_idx:
                # コードの音名リストを取得
                notes = CHORDS[chord] if isinstance(chord, str) else chord
                
                wave_chord = NoteUtils.generate_waveform(
                    notes,
                    play_duration,
                    self.waveform,
                    sample_rate
                )
                
                # コードは音符数で割って正規化
                wave_chord = wave_chord / len(notes)
                
                # 長さを調整
                target_len = end_idx - start_idx
                if len(wave_chord) > target_len:
                    wave_chord = wave_chord[:target_len]
                elif len(wave_chord) < target_len:
                    wave_chord = np.pad(wave_chord, (0, target_len - len(wave_chord)), 'constant')
                
                wave[start_idx:end_idx] += wave_chord * self.volume
            
            current_time += chord_duration
        
        return wave


class Song:
    """楽曲クラス - 複数トラックを管理"""
    
    def __init__(self, tempo=120):
        self.tempo = tempo
        self.tracks = []
    
    def add_track(self, track):
        """トラックを追加"""
        self.tracks.append(track)
        return self
    
    def add_melody(self, notes, durations, style='normal', volume=0.2, waveform='sine'):
        """メロディトラックを追加"""
        track = MelodyTrack(notes, durations, self.tempo, style, volume)
        self.tracks.append(track)
        return self
    
    def add_chords(self, chords, durations, style='normal', volume=0.15, waveform='sine'):
        """コードトラックを追加"""
        track = ChordTrack(chords, durations, self.tempo, style, volume, waveform)
        self.tracks.append(track)
        return self
    
    def render(self, sample_rate=SAMPLE_RATE):
        """全トラックをミックス"""
        if not self.tracks:
            return np.array([])
        
        # 全体の長さを計算
        total_duration = 0
        for track in self.tracks:
            track_duration = sum(d * (60.0 / track.tempo) for d in track.durations)
            total_duration = max(total_duration, track_duration)
        
        # 全体の時間軸
        t = np.linspace(0, total_duration, int(sample_rate * total_duration), False)
        wave_total = np.zeros_like(t)
        
        # 各トラックをレンダリングして加算
        for track in self.tracks:
            wave_track = track.render(total_duration, sample_rate)
            wave_total += wave_track
        
        # 正規化
        max_amp = np.max(np.abs(wave_total))
        if max_amp > 1.0:
            wave_total = wave_total / max_amp * 0.9
        
        return wave_total
    
    def play(self, sample_rate=SAMPLE_RATE):
        """再生"""
        wave = self.render(sample_rate)
        
        with AudioPlayer(sample_rate) as player:
            player.play_wave(wave, volume=1.0, envelope=(0, 0))
        
        return self
    
    def save(self, filename, sample_rate=SAMPLE_RATE):
        """WAVファイルに保存"""
        from scipy.io import wavfile
        
        wave = self.render(sample_rate)
        wave_int16 = (wave * 32767).astype(np.int16)
        wavfile.write(filename, sample_rate, wave_int16)
        print(f"Saved to {filename}")
        return self


# 使用例
if __name__ == "__main__":
    # きらきら星
    melody = ['C4', 'C4', 'G4', 'G4', 'A4', 'A4', 'G4',
              'F4', 'F4', 'E4', 'E4', 'D4', 'D4', 'C4']
    melody_rhythm = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0,
                     0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0]
    
    # コード進行
    chords = ['C', 'G', 'Am', 'F', 'C', 'G', 'F', 'C']
    chord_rhythm = [2, 2, 2, 2, 2, 2, 2, 2]
    
    print("=== オブジェクト指向版 ===")
    
    # メロディのみ
    print("\n1. メロディのみ")
    Song(tempo=120)\
        .add_melody(melody, melody_rhythm, style='normal', volume=0.2)\
        .play()
    
    time.sleep(1)
    
    # コードのみ
    print("\n2. コードのみ")
    Song(tempo=120)\
        .add_chords(chords, chord_rhythm, style='normal', volume=0.15)\
        .play()
    
    time.sleep(1)
    
    # メロディ + コード
    print("\n3. メロディ + コード（同時）")
    Song(tempo=120)\
        .add_melody(melody, melody_rhythm, style='normal', volume=0.2)\
        .add_chords(chords, chord_rhythm, style='normal', volume=0.15, waveform='sine')\
        .play()
    
    # 違うスタイルの組み合わせ
    time.sleep(1)
    print("\n4. メロディ（ノーマル）+ コード（スタッカート）")
    Song(tempo=120)\
        .add_melody(melody, melody_rhythm, style='normal', volume=0.2)\
        .add_chords(chords, chord_rhythm, style='staccato', volume=0.15)\
        .play()
    
    # 保存機能
    # song = Song(tempo=120)\
    #     .add_melody(melody, melody_rhythm, style='normal')\
    #     .add_chords(chords, chord_rhythm, style='normal')\
    #     .save('twinkle.wav')
