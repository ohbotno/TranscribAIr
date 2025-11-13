# Changelog

All notable changes to TranscribAIr will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-11-13

### Fixed
- CI/CD workflow: Fixed Unicode encoding errors in Windows GitHub Actions (cp1252 codec)
- Replaced all Unicode checkmarks (✓) and crosses (✗) with ASCII equivalents ([OK], [ERROR])
- Added UTF-8 encoding environment variable to workflow steps
- Build and installation scripts now work correctly on Windows CI runners

## [1.0.1] - 2025-11-13

### Fixed
- CI/CD workflow: Fixed FFmpeg installation failing in GitHub Actions due to interactive prompts
- Added automatic CI environment detection in `install_ffmpeg.py` and `build.py`
- Enhanced `install_ffmpeg.py` to auto-detect CI environments (GITHUB_ACTIONS, CI env vars)
- Build script now handles non-interactive environments gracefully

## [1.0.0] - 2025-11-13

### Added
- Excel rubric import functionality for easy rubric creation
- Structured feedback mode with custom instruction prompts
- Enhanced feedback display with organized presentation
- Automated setup scripts (setup.bat/setup.sh) for one-click installation
- Quick launch scripts (run.bat/run.sh) for easy application startup
- PyInstaller build system for standalone executable distribution
- Automatic FFmpeg installation and management
- Support for multiple LLM providers (Ollama, OpenAI, Anthropic)
- Multiple Whisper model sizes (tiny, base, small, medium, large)
- Audio recording and file upload transcription modes
- Rubric-based feedback organization
- Export to PDF and Word formats
- Python 3.13 compatibility fixes
- Modern Python packaging with pyproject.toml
- Professional Windows installer with Inno Setup
- Auto-update capability with GitHub Releases integration
- Version display in application
- Optimized executable build for smaller file size
- CI/CD pipeline for automated releases
- Comprehensive development documentation

### Changed
- Initial public release version

### Fixed
- Python 3.13 compatibility issues

## [Unreleased]

### Added
- Future features will be listed here

---

For older changes, see git commit history.
