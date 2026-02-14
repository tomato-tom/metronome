import numpy as np
import pyaudio
import time

SAMPLE_RATE = 44100
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def normalize_note_name(note):
    """フラットをシャープに変換（例：'Bb' → 'A#'）"""
    flat_to_sharp = {
        'Cb': 'B',
        'Db': 'C#',
        'Eb': 'D#',
        'Fb': 'E',
        'Gb': 'F#',
        'Ab': 'G#',
        'Bb': 'A#',
        'E#': 'F',
        'B#': 'C'
    }
    return flat_to_sharp.get(note, note)

def build_chord(chord_symbol, bass_octave=2, chord_octave=4, intervals=None):
    """
    コードをインターバルから生成
    
    Args:
        chord_symbol: 'C', 'Am', 'D7', ...
        bass_octave: ベースのオクターブ（デフォルト2）
        chord_octave: コードのオクターブ（デフォルト4）
        intervals: インターバルリスト（デフォルトはメジャートライアド）
    
    Returns:
        コード構成音のリスト
    """
    result = parse_chord_symbol(chord_symbol)
    root = result[0]

    if intervals is None:
        intervals = result[1]
    
    # ルート名を正規化してインデックス取得
    root = normalize_note_name(root)
    root_index = NOTE_NAMES.index(root)

    chord_notes = []
    
    # ベース音
    chord_notes.append(f"{root}{bass_octave}")
    
    # コード構成音
    for interval in intervals:
        note_index = (root_index + interval) % 12
        note_name = NOTE_NAMES[note_index]
        
        # オクターブ計算
        octave = chord_octave + ((root_index + interval) // 12)
        chord_notes.append(f"{note_name}{octave}")
    
    return chord_notes

def parse_chord_symbol(chord_symbol):
    """
    コードシンボルを解析してroot, interval取得
    
    対応:
        'C', 'Cm', 'Cdim', 'Caug', 'C7', 'Cm7', 'CM7', 'Cm7b5', 'Cdim7', etc.
    """
    # ルートの抽出
    if len(chord_symbol) > 1 and chord_symbol[1] == '#':
        root = chord_symbol[:2]
        suffix = chord_symbol[2:]
    else:
        root = chord_symbol[0]
        suffix = chord_symbol[1:]
    
    # コードタイプの判定
    if suffix == '':
        intervals = [0, 4, 7]  # メジャー
    elif suffix == 'm':
        intervals = [0, 3, 7]  # マイナー
    elif suffix == 'dim':
        intervals = [0, 3, 6]  # ディミニッシュ
    elif suffix == 'aug':
        intervals = [0, 4, 8]  # オーギュメント
    elif suffix == '7':
        intervals = [0, 4, 7, 10]  # セブンス
    elif suffix == 'm7':
        intervals = [0, 3, 7, 10]  # マイナーセブンス
    elif suffix == 'M7' or suffix == 'maj7':
        intervals = [0, 4, 7, 11]  # メジャーセブンス
    elif suffix == 'm7b5':
        intervals = [0, 3, 6, 10]  # マイナーセブンスフラットファイブ
    elif suffix == 'dim7':
        intervals = [0, 3, 6, 9]  # ディミニッシュセブンス
    else:
        intervals = [0, 4, 7]  # デフォルトはメジャー
    
    return root, intervals

def notes_to_midi(notes):
    """
    音名リストをMIDIノート番号に変換
    
    Args:
        notes: ['C2', 'C4', 'E4', 'G4'] のようなコードやメロディのリスト
    
    Returns:
        MIDIノート番号のリスト [36, 60, 64, 67]
    """
    midi_notes = []
    for note_name in notes:
        # ノート名を正規化
        note_name = normalize_note_name(note_name)

        # ノート名とオクターブに分離
        if len(note_name) == 2:  # C4 のような形式
            note = note_name[0]
            octave = int(note_name[1])
        elif len(note_name) == 3:  # C#4 のような形式
            note = note_name[:2]
            octave = int(note_name[2])
        else:
            raise ValueError(f"無効なノート名: {note_name}")
        
        # MIDIノート番号 = ノートインデックス + (オクターブ+1)*12
        note_index = NOTE_NAMES.index(note)
        midi_notes.append(note_index + (octave + 1) * 12)
    
    return midi_notes

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
        chords: コードのリスト（各要素はコードシンボルのリスト）
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
        notes = build_chord(chord)
        
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

# 使用例
if __name__ == "__main__":
    print("=== melody ===")
    melody = ['C', 'D', 'E', 'F', 'G']
    duration = [1, 1, 1, 1, 2]
    play_melody(melody, duration,tempo=180, style='normal')
    time.sleep(1)

    print("=== コード進行（ノーマル）===")
    progression = ['CM7', 'G7', 'Am7', 'FM7', 'CM7']
    duration = [2, 2, 2, 2, 4]
    play_chord(progression, duration,tempo=120, style='normal', waveform='sine')
    time.sleep(1)
    
    #print("\n=== コード進行（レガート＋スクエア波）===")
    #progression = ['C', 'Am', 'Dm', 'G7', 'C']
    #duration = [2, 2, 2, 2, 4]
    #play_chord(progression, duration,tempo=80, style='legato', waveform='square', volume=0.2)
