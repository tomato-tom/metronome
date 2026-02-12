NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def build_chord(chord_symbol, bass_octave=2, chord_octave=4, intervals=None):
    """
    コードをインターバルから生成
    
    Args:
        chord_symbol: 'C', 'Am', 'D7', ...
        bass_octave: ベースのオクターブ（デフォルト2）
        chord_octave: コードのオクターブ（デフォルト4）
        intervals: インターバルリスト（デフォルトはメジャートライアド）
        include_root_octave: ルートの1オクターブ上を含めるか
    
    Returns:
        コード構成音のリスト
    """
    result = parse_chord_symbol(chord_symbol)
    root = result[0]

    if intervals is None:
        intervals = result[1]
    
    if len(root) > 1 and root[1] == '#':
        root_index = NOTE_NAMES.index(root[:2])
    else:
        root_index = NOTE_NAMES.index(root[0])
    chord_notes = []
    
    # ベース音（ルートのbass_octave）
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

# 使用例
if __name__ == "__main__":
    # メジャーコード
    print("C:", build_chord('C'))
    print("G7:", build_chord('G7'))
    
    # オクターブ指定
    print("C (bass octave 1, chord octave 3):", 
          build_chord('C', bass_octave=1, chord_octave=3))
    
    # カスタムインターバル（例：C6）
    print("C6:", build_chord('C6', intervals=[0, 4, 7, 9]))
