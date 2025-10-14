# Quick Start Guide

## First Time Setup

### Windows (Easiest)
1. Double-click `setup.bat`
2. Wait for installation (downloads ~500MB)
3. Double-click `run.bat` to start

### Linux/macOS
```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

## What Gets Installed?

The setup creates a **virtual environment** in the `venv/` folder with:
- ✓ All Python dependencies (transcription + LLM providers)
- ✓ FFmpeg (for audio processing)
- ✓ Whisper models (downloaded on first use)

**Everything is self-contained** - no system-wide installations!

## Optional: Feedback Organization Feature

For AI-powered feedback organization, install **one** of these (after main setup):

**Ollama** (Recommended - Free & Local):
1. Download from [ollama.ai](https://ollama.ai)
2. Install Ollama
3. Run: `ollama pull llama2`
4. Configure in app Settings

**OR use Cloud Providers:**
- Get API key from OpenAI or Anthropic
- Configure in app Settings

## Daily Use

### Windows
- Double-click `run.bat`

### Linux/macOS
```bash
./run.sh
```

### Manual
```bash
# Windows
venv\Scripts\activate
python app.py

# Linux/macOS
source venv/bin/activate
python app.py
```

## First Use - Basic Transcription

1. **Select a model** (recommended: "base" for balanced speed/accuracy)
2. **Click "Load Model"** (downloads ~140MB for base model, one-time only)
3. **Upload a file** OR **record audio**
4. **Click "Transcribe"**
5. **View transcript** in left panel
6. **Save or copy** your transcript

## Using Feedback Organization (For Teachers)

1. **Click Settings** ⚙️ in header → Configure LLM provider
2. **Select Rubric** button → Create rubric with assessment criteria
3. **Record** verbal feedback while reviewing student work
4. **Transcribe** → Raw transcript appears on left
5. **Organize** → AI organizes feedback by rubric (right panel)
6. **Export** → Copy to clipboard or save as PDF/Word

## What is a Virtual Environment?

A virtual environment (`venv/`) is an isolated Python installation that:
- Keeps dependencies separate from your system Python
- Prevents conflicts with other Python projects
- Can be deleted anytime (just delete the `venv/` folder)

## Disk Space Requirements

- **Setup**: ~500MB (Python packages + LLM support)
- **FFmpeg**: ~100MB
- **Whisper Models**:
  - tiny: 75 MB
  - base: 140 MB (recommended)
  - small: 460 MB
  - medium: 1.5 GB
  - large: 2.9 GB
- **LLM Models** (optional, if using Ollama):
  - llama2: ~3.8 GB
  - mistral: ~4.1 GB

Total for typical setup:
- Basic (transcription only): ~750MB
- With feedback (Ollama): ~4.5GB

## Troubleshooting

### Setup fails
```bash
# Try manual setup
python setup.py
```

### Can't run the app
```bash
# Windows
venv\Scripts\python.exe app.py

# Linux/macOS
venv/bin/python app.py
```

### Want to start fresh?
1. Delete the `venv/` folder
2. Run `setup.bat` or `./setup.sh` again

### Need to update?
```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install --upgrade -r requirements.txt
```

## Advanced

### Install additional packages
```bash
# Activate venv first
pip install <package-name>
```

### Build executable
```bash
# Activate venv first
pip install pyinstaller
python build.py
# Find .exe in dist/ folder
```

### Uninstall
1. Delete the entire project folder
2. Delete `%USERPROFILE%\.transribair` (Windows) or `~/.transribair` (Linux/Mac)

That's it! Everything is contained in these two locations.
