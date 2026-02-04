#!/bin/bash
# ベース音名クイズ

# 色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 弦の基本音
declare -A STRING_NOTES
STRING_NOTES[4]="E"
STRING_NOTES[3]="A"
STRING_NOTES[2]="D"
STRING_NOTES[1]="G"

# 音階（半音順）
NOTES=("C" "C#" "D" "D#" "E" "F" "F#" "G" "G#" "A" "A#" "B")

# 別名対応
declare -A NOTE_ALIASES
NOTE_ALIASES["C#"]="Db"
NOTE_ALIASES["D#"]="Eb"
NOTE_ALIASES["F#"]="Gb"
NOTE_ALIASES["G#"]="Ab"
NOTE_ALIASES["A#"]="Bb"

# スコア変数
SCORE=0
TOTAL_QUESTIONS=0
QUIZ_MODE="normal"

# 指定された弦とフレットから音名を取得
get_note_from_position() {
    local string_num=$1
    local fret=$2
    
    if [[ ! "1 2 3 4" =~ $string_num ]] || [[ $fret -lt 0 ]] || [[ $fret -gt 20 ]]; then
        echo ""
        return 1
    fi
    
    local open_note=${STRING_NOTES[$string_num]}
    
    # 開放弦の音のインデックスを探す
    local open_index=-1
    for i in "${!NOTES[@]}"; do
        if [[ "${NOTES[$i]}" == "$open_note" ]]; then
            open_index=$i
            break
        fi
    done
    
    if [[ $open_index -eq -1 ]]; then
        echo ""
        return 1
    fi
    
    # フレット分移動（12音循環）
    local note_index=$(( (open_index + fret) % 12 ))
    echo "${NOTES[$note_index]}"
}

# 答えをチェック
check_answer() {
    local user_answer=$1
    local correct_note=$2
    
    # 大文字に変換
    user_answer=$(echo "$user_answer" | sed 's/^\([a-z]\)/\U\1/')
    
    [[ "$user_answer" == "$correct_note" ]] && return 0  # 正解
    [[ "$user_answer" == "${NOTE_ALIASES[$correct_note]}" ]] && return 0  # 別名で正解
    
    return 1  # 不正解
}

# ランダムな問題を生成
generate_question() {
    local string_num
    local fret
    
    string_num=$(( RANDOM % 4 + 1 ))  # 1-4
    
    # 問題数に応じて難易度調整
    if [[ $TOTAL_QUESTIONS -lt 5 ]]; then
        fret=$(( RANDOM % 6 ))        # 0-5
    elif [[ $TOTAL_QUESTIONS -lt 10 ]]; then
        fret=$(( RANDOM % 13 ))       # 0-12
    else
        fret=$(( RANDOM % 21 ))       # 0-20
    fi
    
    echo "$string_num $fret"
}

# スコア表示
show_score() {
    echo "========================================"
    echo "SCORE: $SCORE/$TOTAL_QUESTIONS"
    if [[ $TOTAL_QUESTIONS -gt 0 ]]; then
        local percentage=$(echo "scale=1; $SCORE * 100 / $TOTAL_QUESTIONS" | bc)
        echo "ACCURACY: ${percentage}%"
    fi
    echo "========================================"
}

# 通常クイズモード
run_normal_quiz() {
    local num_questions=$1
    
    clear
    echo "========================================"
    echo "BASS NOTE QUIZ"
    echo "========================================"
    echo "Answer the note for given string and fret"
    echo "Example: 'G'"
    echo "Commands: 'q'=quit, 'h'=hint, 's'=show score"
    echo "========================================"
    tput sc

    for ((i=1; i<=num_questions; i++)); do
        tput rc
        tput ed
        echo ""
        echo "QUESTION $i/$num_questions"
        
        # 問題生成
        read string_num fret <<< $(generate_question)
        local correct_note=$(get_note_from_position "$string_num" "$fret")
        
        echo "String: $string_num, Fret: $fret"
        
        while true; do
            echo -n "Note?: "
            read user_input
            
            case "$user_input" in
                q|quit|exit)
                    echo "Quitting quiz..."
                    show_score
                    return 1
                    ;;
                h|hint)
                    echo "Hint: String $string_num open note is '${STRING_NOTES[$string_num]}'"
                    continue
                    ;;
                s|score)
                    show_score
                    continue
                    ;;
                "")
                    echo "Please enter a note name."
                    continue
                    ;;
                *)
                    # 答えをチェック
                    if check_answer "$user_input" "$correct_note"; then
                        echo
                        echo -e "${GREEN}CORRECT!${NC}"
                        SCORE=$((SCORE + 1))
                    else
                        echo -e "${RED}WRONG.${NC} Correct answer: '$correct_note'"
                        echo
                    fi

                    read -s -t 1
                    break
                    ;;
            esac
        done
        
        TOTAL_QUESTIONS=$((TOTAL_QUESTIONS + 1))
    done
    
    echo
    show_score
}

# 練習モード
run_practice_mode() {
    clear
    echo "========================================"
    echo "BASS PRACTICE MODE"
    echo "========================================"
    echo "Practice specific positions"
    echo "Format: string-fret (ex: 4-3)"
    echo "Commands: 'q'=quit, 'm'=back to menu"
    echo "========================================"
    
    while true; do
        echo ""
        echo -n "Enter position (string-fret) or command: "
        read input
        
        case "$input" in
            q|quit|exit)
                echo "Exiting practice mode..."
                return 0
                ;;
            m|menu)
                echo "Returning to main menu..."
                return 0
                ;;
            *)
                # フォーマットチェック: string-fret
                if [[ "$input" =~ ^([1-4])-([0-9]+)$ ]]; then
                    local string_num=${BASH_REMATCH[1]}
                    local fret=${BASH_REMATCH[2]}
                    
                    if [[ $fret -gt 20 ]]; then
                        echo "Fret should be 0-20"
                        continue
                    fi
                    
                    local note=$(get_note_from_position "$string_num" "$fret")
                    
                    if [[ -n "$note" ]]; then
                        echo "String $string_num, Fret $fret: $note"
                        
                        # 別名がある場合
                        if [[ -n "${NOTE_ALIASES[$note]}" ]]; then
                            echo "Also known as: ${NOTE_ALIASES[$note]}"
                        fi
                        
                        # 同じ音の他の位置を探す
                        echo "Same note on other positions:"
                        find_same_notes "$note"
                    else
                        echo "Invalid position"
                    fi
                else
                    echo "Invalid format. Use: string-fret (ex: 4-3)"
                fi
                ;;
        esac
    done
}

# 同じ音の他の位置を探す
find_same_notes() {
    local target_note=$1
    local found=0
    
    for s in 1 2 3 4; do
        for f in {0..12}; do
            local note=$(get_note_from_position "$s" "$f")
            if [[ "$note" == "$target_note" ]]; then
                echo "  String $s, Fret $f"
                found=1
            fi
        done
    done
    
    if [[ $found -eq 0 ]]; then
        echo "  (No other positions found within 12 frets)"
    fi
}

# 特定の弦の練習モード
run_string_practice() {
    clear
    echo "========================================"
    echo "SINGLE STRING PRACTICE MODE"
    echo "========================================"
    
    echo -n "Which string to practice? (1-4): "
    read string_choice
    
    if [[ ! "$string_choice" =~ ^[1-4]$ ]]; then
        echo "Invalid string number. Returning to menu."
        return
    fi
    
    echo -n "How many questions? (default 10): "
    read num_questions
    num_questions=${num_questions:-10}
    
    if [[ ! "$num_questions" =~ ^[0-9]+$ ]] || [[ $num_questions -le 0 ]]; then
        num_questions=10
    fi
    
    clear
    echo "========================================"
    echo "PRACTICING STRING $string_choice"
    echo "========================================"
    echo "Open note: ${STRING_NOTES[$string_choice]}"
    echo "Questions: $num_questions"
    echo "Commands: 'q'=quit, 's'=show score"
    echo "========================================"
    
    local local_score=0
    local local_total=0
    
    for ((i=1; i<=num_questions; i++)); do
        echo ""
        echo "Question $i/$num_questions"
        
        # フレットをランダムに選択 (0-12)
        local fret=$(( RANDOM % 13 ))
        local correct_note=$(get_note_from_position "$string_choice" "$fret")
        
        echo "String: $string_choice, Fret: $fret"
        
        while true; do
            echo -n "Note? (ex: C, F#, Bb): "
            read user_input
            
            case "$user_input" in
                q|quit|exit)
                    echo "Quitting practice..."
                    echo "Your score: $local_score/$local_total"
                    return
                    ;;
                s|score)
                    echo "Current score: $local_score/$local_total"
                    continue
                    ;;
                *)
                    if check_answer "$user_input" "$correct_note"; then
                        echo -e "${GREEN}CORRECT!${NC}"
                        local_score=$((local_score + 1))
                        break
                    else
                        echo -e "${RED}WRONG.${NC} Correct answer: '$correct_note'"
                        break
                    fi
                    ;;
            esac
        done
        
        local_total=$((local_total + 1))
    done
    
    echo ""
    echo "========================================"
    echo "PRACTICE COMPLETE"
    echo "Final score: $local_score/$local_total"
    if [[ $local_total -gt 0 ]]; then
        local percentage=$(echo "scale=1; $local_score * 100 / $local_total" | bc)
        echo "Accuracy: ${percentage}%"
    fi
    echo "========================================"
    echo -n "Press Enter to continue..."
    read
}

# TUI風メインメニュー
show_menu() {
    local menu=(
        "Normal Quiz"
        "Practice Mode (by position)"
        "Single String Practice"
        "Show Fretboard Reference"
        "Exit"
    )
    local selected=0
    local key

    tput civis
    clear
    echo "========================================"
    echo "BASS NOTE TRAINER - MAIN MENU"
    echo "========================================"
    tput sc

    while true; do
        tput rc
        tput ed

        for i in "${!menu[@]}"; do
            if [ $i -eq $selected ]; then
                echo "→ ${menu[$i]}"
            else
                echo "  ${menu[$i]}"
            fi
        done
        
        read -rsn1 key
        case "$key" in
            k) ((selected > 0)) && ((selected--)) ;;  # k ↑
            j) ((selected < ${#menu[@]}-1)) && ((selected++)) ;; # j ↓
            $'\x1b')
                read -rsn2 key
                case "$key" in
                    '[A') ((selected > 0)) && ((selected--)) ;;  # ↑
                    '[B') ((selected < ${#menu[@]}-1)) && ((selected++)) ;; # ↓
                esac
                # 特殊キーは３文字シーケンスだから、残りの２文字'n2'を読み取る
                # ↑: \x1b [ A  (ESC + [ + A)
                ;;
            '') # Enter
                echo

                case "$selected" in
                    0)
                        echo -n "How many questions? (default 10): "
                        read num_q
                        num_q=${num_q:-10}
                        
                        if [[ "$num_q" =~ ^[0-9]+$ ]] && [[ $num_q -gt 0 ]]; then
                            run_normal_quiz "$num_q"
                        else
                            echo "Invalid number. Using default (10)."
                            run_normal_quiz 10
                        fi
                        
                        echo -n "Press Enter to continue..."
                        read
                        ;;
                    1)
                        run_practice_mode
                        ;;
                    2)
                        run_string_practice
                        ;;
                    3)
                        show_fretboard_reference
                        echo -n "Press Enter to continue..."
                        read
                        ;;
                    4)
                        echo "Goodbye!"
                        exit 0
                        ;;
                esac
                ;;
        esac
    done
}

# フレットボード参照表を表示
show_fretboard_reference() {
    clear
    echo "========================================"
    echo "BASS FRETBOARD REFERENCE (0-12 frets)"
    echo "========================================"
    echo ""
    echo "String | 0   1   2   3   4   5   6   7   8   9   10  11  12"
    echo "-------|----------------------------------------------------"
    
    for s in {1..4}; do
        printf "  %d    | " "$s"
        
        for f in {0..12}; do
            local note=$(get_note_from_position "$s" "$f")
            printf "%-3s " "$note"
        done
        echo ""
    done
    
    echo ""
    echo "========================================"
    echo "NOTE: # = sharp, b = flat"
    echo "Alternate names: C#=Db, D#=Eb, F#=Gb, G#=Ab, A#=Bb"
    echo "========================================"
}

cleanup() {
    tput cnorm
}

trap cleanup EXIT INT TERM

main() {
    if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
        # 色表示が有効かチェック
        if [[ -t 1 ]]; then
            # 対話モードで色を使用
            :
        else
            # パイプやリダイレクト時は色を無効化
            RED=""
            GREEN=""
            YELLOW=""
            BLUE=""
            NC=""
        fi
        
        show_menu
    fi
}

main "$@"
