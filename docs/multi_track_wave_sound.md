# Multi-track Wave Sound Generator - Documentation

## 📊 System Architecture Flowchart

```mermaid
flowchart TD
    %% Main Components
    subgraph Core["🎵 Core Components"]
        NU[NoteUtils] -->|note_to_freq| F[Frequency Conversion]
        NU -->|generate_waveform| W[Waveform Generation]
        NU -->|parse_chord_symbol| P[Chord Parsing]
        NU -->|build_chord| B[Chord Building]
        NU -->|apply_envelope| E[Envelope Application]
    end

    subgraph Tracks["🎼 Track System"]
        T[Track] -->|abstract| MT[MelodyTrack]
        T -->|abstract| CT[ChordTrack]
        MT -->|render| MW[Melody Waveform]
        CT -->|render| CW[Chord Waveform]
    end

    subgraph Audio["🔊 Audio System"]
        AP[AudioPlayer] -->|open| S[Stream]
        AP -->|play_wave| P2[Playback]
        AP -->|close| C[Cleanup]
    end

    subgraph Song["📀 Song Management"]
        SG[Song] -->|add_track| TT[Track List]
        SG -->|render| MX[Mixer]
        SG -->|play| PL[Play]
        SG -->|save| SV[Save to WAV]
    end

    %% Connections
    MW --> MX
    CW --> MX
    MX --> AP
    NU --> MT
    NU --> CT
    SG --> T
```

## 📈 Class Hierarchy Diagram

```mermaid
classDiagram
    class NoteUtils {
        +note_to_freq(note, octave)$ float
        +apply_envelope(wave, attack, release)$ array
        +generate_waveform(notes, duration, waveform)$ array
        +parse_chord_symbol(chord_symbol)$ tuple
        +build_chord(chord_symbol, bass_octave, chord_octave)$ list
        -_generate_single_note(t, freq, waveform)$ array
    }
    
    class Track {
        #tempo
        #style
        #volume
        #beat_duration
        +render(total_duration, sample_rate)*
        #_get_note_length(style_dict)$
    }
    
    class MelodyTrack {
        -notes
        -durations
        -waveform
        -NOTE_LENGTHS
        +render(total_duration, sample_rate)
    }
    
    class ChordTrack {
        -chords
        -durations
        -waveform
        -NOTE_LENGTHS
        +render(total_duration, sample_rate)
    }
    
    class AudioPlayer {
        -sample_rate
        -p
        -stream
        +__enter__()
        +__exit__()
        +open()
        +close()
        +play_wave(wave, volume, envelope)
        +play_silence(duration)
    }
    
    class Song {
        -tempo
        -tracks
        +add_track(track)
        +add_melody(notes, durations, style, volume, waveform)
        +add_chords(chords, durations, style, volume, waveform)
        +render(sample_rate)
        +play(sample_rate)
        +save(filename, sample_rate)
    }
    
    Track <|-- MelodyTrack
    Track <|-- ChordTrack
    Song o-- Track : contains
    NoteUtils <.. MelodyTrack : uses
    NoteUtils <.. ChordTrack : uses
    AudioPlayer <.. Song : uses
```

## 🔄 Audio Generation Process Flow

```mermaid
flowchart LR
    subgraph Input["📝 Input Stage"]
        A1[Melody Notes] --> M1[MelodyTrack]
        A2[Chord Symbols] --> C1[ChordTrack]
        A3[Tempo/BPM] --> T1[Timing Control]
    end

    subgraph Process["⚙️ Processing Stage"]
        direction TB
        B1[Note to Frequency] --> B2[Waveform Generation]
        B2 --> B3[Envelope Application]
        B3 --> B4[Volume Scaling]
    end

    subgraph Mix["🎛️ Mixing Stage"]
        C1[Melody Wave] --> D1[Mixer]
        C2[Chord Wave] --> D1
        D1 --> D2[Normalization]
    end

    subgraph Output["📤 Output Stage"]
        E1[Audio Playback]
        E2[WAV File Export]
    end

    M1 --> B1
    C1 --> B1
    T1 --> B3
    B4 --> C1
    B4 --> C2
    D2 --> E1
    D2 --> E2
```

## 🎵 Note Processing Sequence

```mermaid
sequenceDiagram
    participant User
    participant Song
    participant Track
    participant NoteUtils
    participant AudioPlayer
    
    User->>Song: add_melody(notes, durations)
    Song->>MelodyTrack: create()
    Song->>Song: store track
    
    User->>Song: add_chords(chords, durations)
    Song->>ChordTrack: create()
    Song->>Song: store track
    
    User->>Song: play()
    
    loop For each track
        Song->>Track: render()
        
        alt MelodyTrack
            Track->>NoteUtils: generate_waveform(note)
            NoteUtils->>NoteUtils: note_to_freq()
            NoteUtils->>Track: waveform
        else ChordTrack
            Track->>NoteUtils: build_chord(chord)
            NoteUtils->>NoteUtils: parse_chord_symbol()
            NoteUtils->>Track: note list
            Track->>NoteUtils: generate_waveform(notes)
            NoteUtils->>Track: waveform
        end
        
        Track->>Song: wave data
    end
    
    Song->>Song: mix tracks()
    Song->>AudioPlayer: play_wave(mixed)
    
    AudioPlayer->>NoteUtils: apply_envelope()
    NoteUtils->>AudioPlayer: enveloped wave
    AudioPlayer->>AudioPlayer: output to speakers
    
    AudioPlayer->>Song: complete
    Song->>User: playback finished
```

## 🎸 Chord Processing Flow

```mermaid
flowchart TD
    subgraph Parse["🔍 Chord Parsing"]
        CS[Chord Symbol<br/>e.g., 'Cm7', 'Ddim'] --> ER{Extract Root}
        ER -->|Sharp Note| RN1["C#, F#, etc."]
        ER -->|Natural Note| RN2["C, D, E, etc."]
        RN1 & RN2 --> SP[Extract Suffix]
        SP --> CI{Chord Type}
        
        CI -->|Major| IM[[0, 4, 7]]
        CI -->|Minor| Im[[0, 3, 7]]
        CI -->|7th| I7[[0, 4, 7, 10]]
        CI -->|m7| Im7[[0, 3, 7, 10]]
        CI -->|maj7| IM7[[0, 4, 7, 11]]
        CI -->|dim| Idim[[0, 3, 6]]
        CI -->|aug| Iaug[[0, 4, 8]]
        CI -->|sus4| Isus[[0, 5, 7]]
    end

    subgraph Build["🏗️ Chord Building"]
        R[Root Note Index] --> O[Octave Calculation]
        I[Intervals] --> N[Note Name Generation]
        O & N --> CN[Build Note List]
        CN --> BL[Bass Note + Chord Notes]
    end

    subgraph Generate["🎛️ Waveform Generation"]
        BL --> GW[Generate Waveform]
        GW -->|Sum| CW[Chord Waveform]
        CW -->|Normalize| NW[Normalized Wave]
    end

    CI --> I
    CS --> R
    I --> Build
    R --> Build
```

## ⏱️ Timing and Duration Calculation

```mermaid
flowchart LR
    subgraph Time["⏰ Time Calculations"]
        T[BPM Tempo] -->|60 / BPM| BD[Beat Duration]
        BD -->|× Note Beats| ND[Note Duration]
        ND -->|× Note Length Factor| PD[Play Duration]
        
        Style{Style} -->|Legato 0.98| LF1
        Style -->|Normal 0.78| LF2
        Style -->|Staccato 0.40| LF3
        
        LF1 & LF2 & LF3 --> PD
    end

    subgraph Sample["📊 Sample Index"]
        PD -->|× Sample Rate| TS[Total Samples]
        CT[Current Time] -->|× Sample Rate| SI[Start Index]
        SI -->|+ TS| EI[End Index]
    end
```

## 🎛️ Audio Mixing Process

```mermaid
flowchart TD
    subgraph T1["Track 1: Melody"]
        M1[Note 1] --> W1[Waveform]
        M2[Note 2] --> W2[Waveform]
        M3[Note N] --> WN[Waveform]
        W1 & W2 & WN -->|Sum| MW[Melody Wave]
    end

    subgraph T2["Track 2: Chords"]
        C1[Chord 1] --> WC1[Waveform]
        C2[Chord 2] --> WC2[Waveform]
        C3[Chord N] --> WCN[Waveform]
        WC1 & WC2 & WCN -->|Sum| CW[Chord Wave]
    end

    subgraph Mixer["🎚️ Mixer"]
        MW -->|Volume A| M[Sum]
        CW -->|Volume B| M
        M -->|Σ| MX[Mixed Signal]
        MX -->|Find Peak| P[Peak Detection]
        P -->|> 1.0| N[Normalize]
        N -->|× 0.9| OUT[Output Wave]
        P -->|≤ 1.0| OUT
    end
```

## 📦 Module Dependency Graph

```mermaid
graph TD
    subgraph External["📦 External Dependencies"]
        NP[numpy] -->|array ops| NU
        NP -->|math ops| MW
        PA[pyaudio] -->|audio out| AP
        SC[scipy.io.wavfile] -->|file write| SG
    end

    subgraph Internal["📁 Internal Modules"]
        NU[NoteUtils] --> MT[MelodyTrack]
        NU --> CT[ChordTrack]
        MT --> SG[Song]
        CT --> SG
        SG --> AP[AudioPlayer]
    end

    subgraph Config["⚙️ Configuration"]
        SR[SAMPLE_RATE=44100Hz]
        NN[NOTE_NAMES]
    end

    SR --> NU
    SR --> AP
    NN --> NU
```


## 🔧 Waveform Generation States

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    state "Waveform Generation" as WG {
        [*] --> SelectWaveform
        SelectWaveform --> Sine: sine
        SelectWaveform --> Square: square
        SelectWaveform --> Sawtooth: sawtooth
        SelectWaveform --> Triangle: triangle
        
        Sine --> Generate
        Square --> Generate
        Sawtooth --> Generate
        Triangle --> Generate
        
        Generate --> ApplyEnvelope
        ApplyEnvelope --> [*]
    }
    
    state "Audio Playback" as AP {
        [*] --> OpenStream
        OpenStream --> WriteData
        WriteData --> CloseStream
        CloseStream --> [*]
    }
    
    Idle --> WG: generate_waveform()
    WG --> AP: play_wave()
    AP --> Idle: playback complete
```

## 📋 Processing Pipeline Summary

```mermaid
flowchart LR
    subgraph Stage1["Stage 1: Note Definition"]
        direction TB
        N1[Note Names] --> N2[Frequency]
        N2 --> N3[Raw Wave]
    end
    
    subgraph Stage2["Stage 2: Track Generation"]
        direction TB
        T1[Melody Track] --> T2[Individual Notes]
        T3[Chord Track] --> T4[Chord Voicings]
    end
    
    subgraph Stage3["Stage 3: Mixing"]
        direction TB
        M1[Volume Control] --> M2[Summation]
        M2 --> M3[Normalization]
    end
    
    subgraph Stage4["Stage 4: Output"]
        direction TB
        O1[PCM Conversion] --> O2[Audio Playback]
        O2 --> O3[Speaker]
        O1 --> O4[WAV File]
    end
    
    Stage1 --> Stage2
    Stage2 --> Stage3
    Stage3 --> Stage4
```

## メモ

再生中にノイズはいるようになり、OS再起動でなおった
ganttチャートでピアノロールのようにできる？

