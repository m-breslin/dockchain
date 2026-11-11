#!/usr/bin/env bash
# Post-create script for devcontainer
# Runs automatically after devcontainer is created

set -euo pipefail

echo "🚀 Setting up devcontainer with Oh My Zsh + Powerlevel10k..."

# -----------------------------
# Find zsh (fallback if not found)
# -----------------------------
if command -v zsh >/dev/null 2>&1; then
    ZSH_PATH=$(command -v zsh)
else
    echo "⚠️ zsh not found, defaulting to /usr/bin/zsh"
    ZSH_PATH="/usr/bin/zsh"
fi

echo "🔹 Using zsh path: $ZSH_PATH"

# -----------------------------
# Ensure zsh is default shell for current user
# -----------------------------
if [ -x "$ZSH_PATH" ]; then
    echo "🔹 Setting zsh as default shell..."
    sudo chsh -s "$ZSH_PATH" "$(whoami)" || true
else
    echo "⚠️ zsh executable not found at $ZSH_PATH, skipping chsh"
fi

# -----------------------------
# Ensure /etc/shells includes zsh
# -----------------------------
if [ -f /etc/shells ] && ! grep -q "^$ZSH_PATH$" /etc/shells; then
    echo "🔹 Adding $ZSH_PATH to /etc/shells..."
    echo "$ZSH_PATH" | sudo tee -a /etc/shells > /dev/null
fi

echo ""
echo "✅ DevContainer setup complete!"
echo ""
echo "🎉 Your shell now includes:"
echo "   • Powerlevel10k theme with beautiful icons"
echo "   • Oh My Zsh with git, python, and docker plugins"
echo "   • Custom aliases and zsh configuration"
echo ""
echo "💡 Tip: If you don't see the Powerlevel10k prompt, run: p10k configure"
echo ""
