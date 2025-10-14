# Transcribair

A desktop application for audio transcription powered by OpenAI's Whisper model. Features a modern, user-friendly interface for both file upload and live recording transcription.

## Features

### Core Transcription
- 🎤 **Live Recording**: Record audio directly from your microphone with real-time level monitoring
- 📁 **File Upload**: Support for multiple audio formats (MP3, WAV, M4A, FLAC, OGG, etc.)
- 🤖 **Multiple Model Sizes**: Choose from tiny, base, small, medium, or large Whisper models
- ⏱️ **Optional Timestamps**: Include timestamps in your transcripts
- 🚀 **CPU Optimized**: Uses faster-whisper for efficient CPU-based transcription

### AI-Powered Feedback Organization (NEW)
- 🎯 **Custom Rubrics**: Create assessment rubrics with multiple criteria and weights
- 🧠 **LLM Integration**: Organize verbal feedback using AI (Ollama, OpenAI, or Anthropic)
- 📊 **Side-by-Side View**: See transcript and organized feedback simultaneously
- 💾 **Multiple Export Formats**: Clipboard, Text, Markdown, PDF, and Word documents
- ⚙️ **Flexible Settings**: Auto-organize, detail levels, and provider configuration
- 📚 **Rubric Library**: Save and reuse rubrics across different assignments

### User Interface
- 🖥️ **Modern UI**: Clean, intuitive interface built with CustomTkinter
- 📱 **Responsive Layout**: Adapts to different screen sizes with side-by-side panels
- ⚡ **Quick Actions**: One-click copy, organize, and export

## Installation

### 🚀 Easiest Method: One-Click Setup (Recommended)

**For Windows users:**
1. Download and extract this repository
2. Double-click `setup.bat`
3. Wait for installation to complete
4. Double-click `run.bat` to start Transcribair

**For Linux/macOS users:**
1. Download and extract this repository
2. Open terminal in the project folder
3. Run: `chmod +x setup.sh run.sh`
4. Run: `./setup.sh`
5. Run: `./run.sh` to start Transcribair

The setup script automatically:
- ✓ Creates a virtual environment
- ✓ Installs all Python dependencies (including LLM providers)
- ✓ Downloads and configures FFmpeg
- ✓ Tests the installation

**Optional: For Feedback Organization Feature**
After setup, install Ollama (recommended for local AI) or configure cloud provider API keys:
- **Ollama** (free, runs locally): Download from [ollama.ai](https://ollama.ai), then run `ollama pull llama2`
- **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com)
- **Anthropic**: Get API key from [console.anthropic.com](https://console.anthropic.com)

Configure your chosen provider in the app via the Settings button.

---

### Option 1: Automated Setup (Virtual Environment)

Use this method to keep dependencies isolated in a virtual environment:

```bash
# Install Python 3.9+ from python.org
cd Transcribair
python setup.py
```

Then run:
```bash
# Windows
venv\Scripts\activate
python app.py

# Linux/macOS
source venv/bin/activate
python app.py
```

### Option 2: Manual Installation (System-wide)

If you prefer installing dependencies system-wide:

1. **Install Python 3.9 or higher**
   - Download from [python.org](https://www.python.org/downloads/)

2. **Clone or download this repository**
   ```bash
   cd Transcribair
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   - FFmpeg will be downloaded automatically on first run (if not already installed)

### Option 3: Manual FFmpeg Installation (Optional)

If you prefer to install FFmpeg yourself or the automatic installation fails:

```bash
python install_ffmpeg.py
```

Or install manually:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **Windows (chocolatey)**: `choco install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

### Option 4: Build Standalone Executable

For creating a distributable .exe file:

1. **Run automated setup first**
   ```bash
   python setup.py
   ```

2. **Activate virtual environment and install PyInstaller**
   ```bash
   # Windows
   venv\Scripts\activate
   pip install pyinstaller
   python build.py

   # Linux/macOS
   source venv/bin/activate
   pip install pyinstaller
   python build.py
   ```

3. **Find the executable in `dist/Transcribair.exe`**
   - FFmpeg is bundled inside the executable
   - No additional installation needed for end users!
   - Distribute the entire `dist` folder

## Usage

### First Run

1. Launch Transcribair
2. Select a model size from the dropdown (recommended: **base** for good balance)
3. Click **Load Model** - the model will download automatically on first use
4. Wait for the model to load (larger models take longer)

### Transcribing Files

1. Switch to the **Upload File** tab
2. Click **Browse Files** or drag-and-drop an audio file
3. Optional: Check **Include Timestamps** for timestamped output
4. Click **Transcribe**
5. Wait for processing (time depends on audio length and model size)
6. View, copy, or save the transcript

### Recording Audio

1. Switch to the **Record Audio** tab
2. Select your microphone from the dropdown
3. Click **Start Recording** (red button)
4. Speak into your microphone
5. Click **Stop Recording** when done
6. Optional: Save the recording for later use
7. Click **Transcribe** to generate transcript

### Using Feedback Organization (For Teachers)

**Initial Setup:**
1. Click the **⚙ Settings** button in the header
2. Configure your LLM provider (Ollama recommended for privacy)
3. Optional: Enable "Auto-organize" for hands-free workflow

**Creating a Rubric:**
1. In Record or Upload tab, click **Select Rubric**
2. Click **New Rubric**
3. Add criteria with names, descriptions, and weights
4. Save for future use (rubrics are reusable)

**Recording and Organizing Feedback:**
1. Select your rubric before or after recording
2. Record your verbal feedback while reviewing student work
3. Click **Transcribe** - raw transcript appears on the left
4. Click **Organize** (or automatic if enabled) - AI organizes by rubric criteria on the right
5. Review organized feedback in the right panel
6. Use dropdown to export:
   - **Copy to Clipboard** (paste into LMS)
   - **Save as PDF** (professional format)
   - **Save as Word** (editable document)
   - **Save as Text/Markdown** (portable formats)

### Model Sizes

| Model  | Disk Size | Speed  | Accuracy | Recommended For        |
|--------|-----------|--------|----------|------------------------|
| tiny   | ~75 MB    | Fastest| Lowest   | Quick tests            |
| base   | ~140 MB   | Fast   | Good     | **General use** ⭐     |
| small  | ~460 MB   | Medium | Better   | Higher accuracy needs  |
| medium | ~1.5 GB   | Slow   | High     | Professional use       |
| large  | ~2.9 GB   | Slowest| Highest  | Maximum accuracy       |

## File Formats Supported

- MP3
- WAV
- M4A
- FLAC
- OGG
- AAC
- WMA
- OPUS

## System Requirements

- **OS**: Windows 10/11 (Linux/Mac compatible from source)
- **Python**: 3.9 - 3.13 (includes Python 3.13 compatibility fixes)
- **RAM**: 4GB minimum (8GB+ recommended for larger models and LLM processing)
- **Disk Space**:
  - Application: ~50MB
  - Whisper Models: 75MB - 2.9GB (depending on model selected)
  - LLM Models (if using Ollama): 3.8GB - 7GB per model
  - Recordings & Rubrics: Variable based on usage
- **Microphone**: Required for recording feature
- **Internet**: Required for model downloads and cloud LLM providers (OpenAI/Anthropic)

## Project Structure

```
Transcribair/
├── venv/                    # Virtual environment (created by setup)
├── core/                    # Core transcription engine
├── ui/                      # User interface components
├── app.py                   # Main application
├── python313_fix.py         # Python 3.13 compatibility fix
├── setup.py                 # Automated setup script
├── setup.bat / setup.sh     # One-click setup scripts
├── run.bat / run.sh         # Quick run scripts
├── install_ffmpeg.py        # FFmpeg installer
├── build.py                 # Executable builder
└── requirements.txt         # Python dependencies
```

## Data Storage

- **Virtual Environment**: `venv/` in project folder (if using automated setup)
- **Whisper Models**: `%USERPROFILE%\.transcribair\models` (Windows) or `~/.transcribair/models` (Linux/Mac)
- **Recordings**: `%USERPROFILE%\.transcribair\recordings` (Windows) or `~/.transcribair/recordings` (Linux/Mac)
- **Rubrics**: `%USERPROFILE%\.transcribair\rubrics` (Windows) or `~/.transcribair/rubrics` (Linux/Mac)
- **Settings**: `%USERPROFILE%\.transcribair\settings.json` (Windows) or `~/.transcribair/settings.json` (Linux/Mac)
- **FFmpeg**: `%USERPROFILE%\.transcribair\ffmpeg` (Windows) or `~/.transcribair/ffmpeg` (Linux/Mac)

Whisper models are downloaded once and cached locally for offline use. Rubrics and settings persist between sessions.

## Troubleshooting

### "No microphone detected"
- Check microphone is connected and enabled in Windows settings
- Restart the application after connecting microphone

### "Error loading model"
- Ensure you have sufficient disk space
- Check internet connection (models download on first use)
- Try a smaller model size

### Audio conversion errors
- FFmpeg should install automatically on first run
- If it fails, run: `python install_ffmpeg.py`
- Or install FFmpeg manually (see Installation section)
- Try converting the file to WAV format first

### "FFmpeg not found" error
- The app tries to install FFmpeg automatically
- If automatic installation fails, run: `python install_ffmpeg.py`
- Or install manually from https://ffmpeg.org/download.html
- Restart the application after installing

### Slow transcription
- Use a smaller model (tiny or base)
- Close other applications to free up CPU
- Consider upgrading RAM for larger models

### "Failed to organize feedback" or LLM errors
- **Ollama**: Ensure Ollama is running (`ollama serve`) and model is downloaded (`ollama pull llama2`)
- **OpenAI/Anthropic**: Check API key is correct in Settings
- **Network**: Cloud providers require internet connection
- Try a different LLM provider in Settings

### Feedback organization takes too long
- Use a faster model (llama2 for Ollama, gpt-3.5-turbo for OpenAI)
- Reduce feedback detail level in Settings to "Brief"
- Ensure rubric has reasonable number of criteria (3-7 recommended)

## Credits

- Built with [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- UI powered by [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Transcription by [OpenAI Whisper](https://github.com/openai/whisper)

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions, please open an issue on the project repository.
