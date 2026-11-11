# PyQuant Developer - Dotfiles

Professional dotfiles for PyQuant development → modular Zsh configuration, aliases, functions, and prompt styling for devcontainers and local development.


## Features

- **Zsh Configuration (`.zshrc`)**  
  Central configuration that sources all modular files.

- **Aliases (`aliases.zsh`)**  
  Shortcuts for common Git, Docker, and project commands.

- **Git Configuration (`gitconfig`)**  
  Standardized Git aliases and settings.

- **Copy and Paste Dev Container Setup (`.devcontainer`)**
  Easy to startup development environment for python projects.

---

## Quick Start

### Using with Devcontainer (Recommended)

The dotfiles include full devcontainer support with automatic setup:

1. **Clone the repository** into your workspace:
   ```bash
   git clone <your-repo-url> dotfiles
   cd dotfiles
   ```

2. **Take or Copy .devcontainer:**
   - Copy or Move the .devcontainer folder into the base of your repo
   - In VS Code: Click "Reopen in Container" or if you ever made manual changes "Reopenin Container without Cache" when prompted
   - Or use the command palette: "Dev Containers: Reopen in Container"

3. **That's it!** Everything installs automatically:
   - ✓ Zsh is installed and set as default shell
   - ✓ Oh My Zsh is installed with beautiful configuration
   - ✓ Powerlevel10k theme with icons
   - ✓ All configurations are symlinked
   - ✓ All aliases and functions are ready to use

4. **Optional Step: PowerLevel10k Prompt Wizard:**
   - You can either exit immediately for PyQuant Developer Default
   - Or you can go through the prompt wizard and make personal changes. Just make sure the zsh/.p10k.zsh keeps your new changes.

### 🖥️ Manual Installation (Linux/macOS/WSL)

For local development or non-devcontainer environments:

**Quick Install:**
```bash
git clone https://github.com/PyQuant/dotfiles.git ~/dotfiles
cd ~/dotfiles
bash install.sh
```

**What the install script does:**
- Installs Zsh if not already available
- Installs Oh My Zsh with beautiful defaults
- Installs Powerlevel10k theme for gorgeous terminal icons
- Creates symlinks for all configuration files
- Sets Zsh as your default shell
- Backs up any existing configuration files

**After installation:**
```bash
exec zsh
```

## Configuration

### Zsh Setup

The Zsh configuration is modular and automatically loaded from two possible locations:
- **Symlinked location** (preferred): `~/.config/zsh/`
- **Direct location**: `$DOTFILES/zsh/`

### Git Configuration

The Git configuration is automatically symlinked to `~/.gitconfig`. To customize:

**Edit your git user info:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Powerlevel10k Integration

The dotfiles come with **Powerlevel10k** installed and configured by default. It provides:

- 🎨 Beautiful terminal colors with Nerd Font icons
- 📊 Real-time git status in your prompt
- ⚡ Fast, responsive terminal experience
- 🎯 Customizable prompt segments

**You get it automatically!** Just install the dotfiles and you're ready to go.

**To customize your Powerlevel10k prompt:**
```bash
p10k configure
```

This opens an interactive wizard. For more details, see: [Powerlevel10k Documentation](https://github.com/romkatv/powerlevel10k)

**Note:** Install a Nerd Font for perfect icon display. Recommended: **MesloLGS NF**
- [Download Fonts](https://github.com/romkatv/powerlevel10k#fonts)
- In VS Code: Set `"terminal.integrated.fontFamily": "MesloLGS NF"` in settings

### Devcontainer Customization

This repository includes a **baseline `.devcontainer/devcontainer.json`** designed to work well for most Python projects.  
You are encouraged to **copy and adapt it per project** rather than treating it as a one-size-fits-all file.

Below are recommended adjustments based on common project types.

---

**Core Sections (What They Do)**

```json
{
  "build": { ... },
  "customizations": { ... },
  "postCreateCommand": "...",
  "features": { ... }
}
```

**build** →
Defines the Dockerfile and build context.
Change this when your project needs system dependencies (Node, Java, Postgres client, etc).

**customizations.vscode** →
Controls VS Code extensions and editor defaults inside the container.
This is where you tailor the developer experience per project.

**postCreateCommand** →
Runs once after the container is created.
Ideal for installing dependencies, wiring dotfiles, and initializing tooling.

**features** →
Adds prebuilt capabilities (Docker CLI, GitHub CLI, etc) without bloating your Dockerfile.

**Python Web Applications (Flask / FastAPI / Django)**
Recommended changes:

Add web-related VS Code extensions:
```
"extensions": [
  "ms-python.python",
  "ms-python.debugpy",
  "ms-azuretools.vscode-docker"
]
```

Expose ports in devcontainer.json:
```
"forwardPorts": [8000]
```
Set environment variables:
```
"containerEnv": {
  "FLASK_ENV": "development",
  "PYTHONUNBUFFERED": "1"
}
```

Keep postCreateCommand lightweight (dependency install only):
```
"postCreateCommand": "pip install -r requirements.txt"
```
Tip: Avoid running the web server in postCreateCommand. Use VS Code tasks or docker-compose instead.

**ETL / Data Engineering (Airflow + dbt)**

Recommended changes:

Use docker-compose instead of a single Dockerfile:
```
"dockerComposeFile": ["../docker-compose.yml"],
"service": "airflow"
```
Increase container resources (Airflow is heavy):
```
"runArgs": ["--memory=8g"]
```
Add extensions useful for SQL and YAML:
```
"extensions": [
  "ms-python.python",
  "innoverio.vscode-dbt-power-user",
  "redhat.vscode-yaml"
]
```
Keep Airflow initialization out of postCreateCommand.
Prefer:
```
Makefile

docker-compose up

explicit setup scripts
```
Rule of thumb: postCreateCommand prepares the developer, not the pipeline.


### Contributing

To contribute improvements to the dotfiles:

1. Create a feature branch
2. Make your changes
3. Test your changes locally and in a devcontainer
4. Submit a pull request

## License

These dotfiles are provided as-is for the PyQuant Platform.

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review the included configuration files for advanced customization
- Contact the PyQuant Platform team
