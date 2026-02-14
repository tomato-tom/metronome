import fluidsynth
import time

# FluidSynth初期化
fs = fluidsynth.Synth()
fs.start(driver="alsa")

# SoundFontロード
sfid = fs.sfload("/usr/share/sounds/sf3/default-GM.sf3")

instruments = {
    'piano': 0,
    'bass': 32,
    'violin': 40,
    'sax': 65,
    'flute': 73,
    'synth': 80,
}

fs.program_select(0, sfid, 0, instruments['piano'])

# 音量
fs.cc(0, 7, 127)  # ボリューム
fs.cc(0, 11, 127) # エクスプレッション

def play_melody(notes, durations, speed=1.0, volume_boost=1.0):
    """メロディを再生"""
    
    for note, dur in zip(notes, durations):
        # 速度調整
        actual_duration = dur / speed
        
        # 音量調整
        velocity = min(127, int(80 * volume_boost))  # 基本80
        
        fs.noteon(0, note, velocity)
        time.sleep(actual_duration * 0.8)  # ノート長
        fs.noteoff(0, note)
        time.sleep(actual_duration * 0.2)  # 休符
        
    print("完了")

# メリーさんの羊
notes = [64, 62, 60, 62,
         64, 64, 64,
         62, 62, 62,
         64, 67, 67]

durations = [0.75, 0.25, 0.5, 0.5,
             0.5, 0.5, 1.0,
             0.5, 0.5, 1.0,
             0.5, 0.5, 1.0]

play_melody(notes, durations, speed=2.5, volume_boost=1.5)

fs.delete()
