# TranscribAIr

[![Version](https://img.shields.io/badge/version-1.0.5-blue.svg)](https://github.com/otherworld-dev/TranscribAIr/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

AI-powered audio transcription with intelligent feedback organization for educators. Built with OpenAI Whisper and local/cloud LLMs.

## ✨ Features

- **Transcription**: Record or upload audio → accurate text (5 model sizes available)
- **Smart Feedback**: Organize verbal feedback by rubric criteria using AI
- **Excel Import**: Import existing rubrics from spreadsheets
- **Multi-Format Export**: PDF, Word, Markdown, or Clipboard
- **LLM Support**: Ollama (local), OpenAI, or Anthropic
- **Modern UI**: Clean interface with side-by-side transcript/feedback view

## 🚀 Quick Start

### For End Users

**[Download from Releases](https://github.com/otherworld-dev/TranscribAIr/releases/latest)** - Get the latest Windows executable or installer

### For Developers

```bash
# Clone repository
git clone https://github.com/otherworld-dev/TranscribAIr.git
cd TranscribAIr

# Windows: One-click setup
setup.bat && run.bat

# Linux/macOS: One-click setup
chmod +x setup.sh run.sh && ./setup.sh && ./run.sh

# Or install as package
pip install -e .
transcribair
```

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Release Process](.claude/CLAUDE.md)** - For maintainers

## 🎯 Usage

1. **Load Model**: Choose Whisper model size (base recommended)
2. **Record or Upload**: Speak or select audio file
3. **Transcribe**: Get accurate text transcription
4. **Organize** (Optional): Use AI to organize by rubric criteria
5. **Export**: Copy, save as PDF/Word, or export to LMS

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## 💡 Use Cases

- **Educators**: Organize verbal feedback for student work
- **Researchers**: Transcribe interviews and field recordings
- **Content Creators**: Convert audio to text for editing
- **Accessibility**: Generate transcripts for audio content

## 🛠️ System Requirements

- **OS**: Windows 10/11, Linux, or macOS
- **Python**: 3.9 - 3.13
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk**: 500MB app + 75MB-3GB models
- **Optional**: Microphone for recording, GPU for faster processing

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick start for contributors:
```bash
pip install -e ".[dev]"   # Install with dev dependencies
pytest                    # Run tests (when available)
black .                   # Format code
```

## 📜 License

MIT License - see [LICENSE](LICENSE) file.

Copyright © 2025 Swansea University

## 🔗 Links

- **[Releases](https://github.com/otherworld-dev/TranscribAIr/releases)** - Download latest version
- **[Issues](https://github.com/otherworld-dev/TranscribAIr/issues)** - Report bugs or request features
- **[Discussions](https://github.com/otherworld-dev/TranscribAIr/discussions)** - Ask questions or share ideas

## 🙏 Credits

Built with:
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [ReportLab](https://www.reportlab.com/) & [python-docx](https://python-docx.readthedocs.io/) - Document generation

---

**Star ⭐ this repo if you find it useful!**
