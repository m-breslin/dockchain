# -------------------------------------------------
# Base: Python 3.12.7 slim (Debian)
# -------------------------------------------------
FROM python:3.12.7-slim

# -----------------------------
# Define HOME
# -----------------------------
ENV HOME=/root
ENV PATH="$HOME/.local/bin:$HOME/.venv/bin:$PATH"

# -----------------------------
# System setup
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    zsh git curl sudo vim ca-certificates dos2unix openssh-client \
    lsb-release gnupg build-essential \
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Docker CLI
# -----------------------------
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list \
 && apt-get update && apt-get install -y docker-ce-cli \
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# System setup
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    zsh git curl wget sudo vim ca-certificates dos2unix lsb-release gnupg build-essential \
 && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Oh My Zsh via zsh-in-docker
# -----------------------------
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.2.1/zsh-in-docker.sh)" -- \
    -p git \
    -p docker \
    -p python

# -----------------------------
# Install uv (modern Python package manager)
# -----------------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- 0.4.23

# -----------------------------
# Create virtual environment for global tools
# -----------------------------
RUN uv venv $HOME/.venv \
 && $HOME/.venv/bin/python -m ensurepip \
 && $HOME/.venv/bin/python -m pip install --upgrade "pip==23.3.1" \
 && $HOME/.venv/bin/python -m pip install --upgrade "ruff==0.1.15" "pre-commit==3.4.0"

# -----------------------------
# Copy dotfiles from repo root (dotfiles/)
# -----------------------------
COPY dotfiles/zsh/.zshrc $HOME/.zshrc
COPY dotfiles/zsh/aliases.zsh $HOME/aliases.zsh
COPY dotfiles/git/gitconfig $HOME/gitconfig
RUN dos2unix $HOME/.zshrc $HOME/aliases.zsh $HOME/gitconfig || true

# -----------------------------
# Set Zsh as default shell
# -----------------------------
SHELL ["/usr/bin/zsh", "-c"]
CMD ["zsh"]
