#!/bin/bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel)"

# アプリ実行
run() {
    local command="$1"
    shift
    case $command in
        m) bash "$PROJECT_ROOT/metronome.sh" "$@" ;;
        f) bash "$PROJECT_ROOT/fretboard_quiz.sh" ;;
        r) bash "$PROJECT_ROOT/rhythm_pattern.sh" "$@" ;;
        e) python "$PROJECT_ROOT/euclidean_rhythm.py" "$@" ;;
        *)
            echo "usage:"
            echo "source run.sh"
            echo "run [m|f|r|e]"
            ;;
    esac
}

git_diff() {
    case "$1" in
        # gd → ステージされていない変更
        "")
            git diff
            ;;
        # gd s → ステージ済みの変更（index vs HEAD）
        s)
            git diff --cached
            ;;
        # gd 1 → 最後のコミットとの差分（HEAD vs HEAD~1）
        [0-9]*)
            git diff "HEAD~$1"
            ;;
        # gd main → 現在のブランチと指定ブランチの差分
        *)
            if git rev-parse --verify "$1" >/dev/null 2>&1; then
                git diff "$1"
            else
                echo "❓ Unknown argument or branch: $1" >&2
                echo "Usage: gd [branch|commit|--cached|s]" >&2
                return 1
            fi
            ;;
    esac
}

# git_update [target_branch] [message]
# e.g. git_update main "Add files"
git_update() {
    local target_branch=""
    local message=""

    if [ "$1" = main ] || [ "$1" = dev ]; then
        target_branch="$1"
        shift
    fi
    message="${*:-update}"

    current_branch=$(git branch --show-current 2>/dev/null)
    if [ -z "$current_branch" ]; then
        echo "❌ Not in a Git repository." >&2
        return 1
    fi

    # 新規ファイルあったら追加
    if [ -n "$(git status --porcelain)" ]; then
        change_dir=false
        if ! [[ $(pwd) = $PROJECT_ROOT ]]; then
            cd $PROJECT_ROOT
            change_dir=true
        fi
        git add .
        $change_dir && cd -
    fi

    # 変更があるか確認（ステージ前＋ステージ後）
    if git diff --quiet && git diff --cached --quiet; then
        echo "ℹ️ No changes to commit." >&2
        return 0
    fi

    # -- push --
    # main -> local + github
    # dev -> local
    # feature* -> local
    #
    # -- merge --
    # feature* -> dev -> main
    cd "$PROJECT_ROOT"
    if [ "$current_branch" = dev ]; then
        # on dev
        git commit -m "$message"
        git push local dev

        if [ "$target_branch" = main ]; then
            # merge: dev -> main
            git switch main &&
            git merge dev &&
            git push local main &&
            git push github main &&
            git switch dev
        fi
    elif [ "$current_branch" = main ]; then
        # on main
        git merge dev &&
        git push local main &&
        git push github main &&
        git switch dev
    else
        # feature*など
        git commit -m "$message"
        git push local "$current_branch"

        if [ "$target_branch" = dev ]; then
            # merge: feature* -> dev
            git switch dev &&
            git merge "$current_branch" &&
            git push local dev &&
            git switch "$current_branch"
        fi
    fi
    cd -
}

alias gu="git_update"
alias gl="git log --oneline"
alias gd="git_diff"

