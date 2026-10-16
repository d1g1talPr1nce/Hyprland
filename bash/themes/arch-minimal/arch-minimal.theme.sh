#!/usr/bin/env bash

function _arch_minimal_prompt_command() {
    local last_status=$?
    local icon='\[\e[38;5;75m\]󰣇'
    local path='\[\e[38;5;250m\]\w'
    local arrow='\[\e[38;5;79m\]❯'
    local reset='\[\e[0m\]'
    local git_segment=""

    local branch
    branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) ||
        branch=$(git rev-parse --short HEAD 2>/dev/null)

    if [[ -n "$branch" ]]; then
        git_segment=" \[\e[38;5;110m\] ${branch}"
    fi

    local venv_segment=""
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        local venv_name="${VIRTUAL_ENV_PROMPT:-${VIRTUAL_ENV##*/}}"
        venv_segment=" \[\e[38;5;221m\] ${venv_name}"
    fi

    local status_segment=""
    if (( last_status != 0 )); then
        status_segment=" \[\e[38;5;203m\]${last_status}"
    fi

    # Root mode
    if (( EUID == 0 )); then
        icon='\[\e[38;5;196m\]󰣇'
        arrow='\[\e[38;5;196m\]#'
    fi


    PS1="${icon} ${path}${git_segment}${venv_segment}${status_segment} ${arrow} ${reset}"
}

_omb_util_add_prompt_command _arch_minimal_prompt_command
