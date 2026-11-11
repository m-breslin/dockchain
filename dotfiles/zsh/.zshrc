# -------------------------------------------------
# 🌀 Oh My Zsh Setup
# -------------------------------------------------
export ZSH="$HOME/.oh-my-zsh"

# Theme: use Powerlevel10k if available, otherwise fallback
if [ -d "$ZSH/custom/themes/powerlevel10k" ]; then
  ZSH_THEME="powerlevel10k/powerlevel10k"
else
  ZSH_THEME="agnoster"
fi

# Core plugins (light but useful)
plugins=(git python docker)

# Load Oh My Zsh safely
if [ -s "$ZSH/oh-my-zsh.sh" ]; then
  source "$ZSH/oh-my-zsh.sh"
else
  echo "⚠️  Oh My Zsh not found — using basic shell"
fi

# -------------------------------------------------
# 🧰 Environment and Path
# -------------------------------------------------
export PATH="$HOME/.local/bin:$PATH"
export EDITOR="vim"
export PAGER="less"
export TERM="xterm-256color"

# Load aliases if present
[ -f "$HOME/.aliases" ] && source "$HOME/.aliases"

# Load Powerlevel10k config if available
[[ -f "$HOME/.p10k.zsh" ]] && source "$HOME/.p10k.zsh"

# -------------------------------------------------
# 📜 History Configuration
# -------------------------------------------------
HISTFILE="$HOME/.zsh_history"
HISTSIZE=5000
SAVEHIST=5000
setopt HIST_IGNORE_ALL_DUPS SHARE_HISTORY

# -------------------------------------------------
# 🎨 Fallback prompt if Powerlevel10k not active
# -------------------------------------------------
if typeset -f git_prompt_info >/dev/null; then
  PROMPT='%F{cyan}%n@%m%f:%F{yellow}%~%f$(git_prompt_info)%# '
else
  PROMPT='%F{cyan}%n@%m%f:%F{yellow}%~%f %# '
fi

# -------------------------------------------------
# 💬 Welcome Message (interactive shells only)
# -------------------------------------------------
if [[ $- == *i* ]]; then
  echo ""
  echo "∞ Welcome to Your Python Dev Environment ∞"
  echo "🐍 Python 3.12  |  ⚡ uv  |  🧠 zsh  |  🖥️  $(lsb_release -ds 2>/dev/null || echo 'Linux')"
  echo ""
fi
