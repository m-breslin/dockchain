# zsh/aliases.zsh - aliases for Git, Docker, dev workflow

# Quality-of-life shortcuts
alias ll="ls -alF"
alias la="ls -A"
alias l="ls -CF"

# Git helpers
alias gs="git status"
alias ga="git add"
alias gc="git commit -m"
alias gp="git push"
alias gl="git log --oneline --decorate --graph"

# Docker helpers
alias dcu="docker compose up -d"
alias dcd="docker compose down"
alias dcl="docker compose logs -f"
alias dcb="docker compose build"

# Python helpers
alias py="python"
alias pipu="uv pip install -U pip"
alias pytest="python -m pytest -v"

# Misc
alias c="clear"
alias v="vim"