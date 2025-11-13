# Contributing to TranscribAIr

Thank you for considering contributing to TranscribAIr! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project follows standard open-source community guidelines. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.9 - 3.13
- Git
- FFmpeg (automatically installed by setup.py)

### Finding Issues

- Check the [GitHub Issues](https://github.com/otherworld-dev/TranscribAIr/issues) page
- Look for issues tagged with `good first issue` or `help wanted`
- Comment on an issue before starting work to avoid duplication

## Development Setup

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/otherworld-dev/TranscribAIr.git
   cd TranscribAIr
   ```

2. **Run automated setup**
   ```bash
   # Windows
   setup.bat

   # Linux/macOS
   ./setup.sh
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies
   - Install FFmpeg automatically

3. **Activate the virtual environment** (if not already activated)
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

4. **Run the application**
   ```bash
   # Windows
   run.bat

   # Linux/macOS
   ./run.sh
   ```

### Development Install

For development, install in editable mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

This installs:
- PyInstaller (for building executables)
- pytest (for testing)
- black (for code formatting)
- flake8 (for linting)
- mypy (for type checking)

## Project Structure

```
TranscribAIr/
├── app.py                 # Main entry point
├── __version__.py         # Version information
├── core/                  # Core business logic
│   ├── transcriber.py     # Whisper transcription
│   ├── recorder.py        # Audio recording
│   ├── feedback.py        # LLM feedback organization
│   ├── rubric.py          # Rubric management
│   ├── settings.py        # Settings persistence
│   ├── export.py          # PDF/Word export
│   └── excel_import.py    # Excel rubric import
├── ui/                    # UI components
│   ├── main_window.py     # Main application window
│   ├── upload_tab.py      # File upload interface
│   ├── record_tab.py      # Recording interface
│   ├── settings_dialog.py # Settings UI
│   ├── rubric_dialog.py   # Rubric editor
│   └── feedback_panel.py  # Feedback display
├── tests/                 # Test files (to be added)
├── build.py               # PyInstaller build script
├── build.spec             # PyInstaller specification
├── installer.iss          # Inno Setup installer script
└── pyproject.toml         # Modern Python packaging config
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation (configured in .editorconfig)
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Code Formatting

We use `black` for automatic code formatting:

```bash
black .
```

### Linting

Run `flake8` to check for code issues:

```bash
flake8 core ui app.py
```

### Type Checking

Run `mypy` for type checking:

```bash
mypy core ui app.py
```

### Naming Conventions

- **Files**: snake_case (e.g., `audio_utils.py`)
- **Classes**: PascalCase (e.g., `FeedbackOrganizer`)
- **Functions/Methods**: snake_case (e.g., `load_model()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private members**: Prefix with underscore (e.g., `_internal_method()`)

## Testing

### Running Tests

```bash
pytest
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix (e.g., `test_transcriber.py`)
- Use descriptive test names (e.g., `test_transcribe_with_timestamps()`)
- Test both success and failure cases
- Mock external dependencies (LLM APIs, file system when appropriate)

Example test:

```python
def test_transcriber_loads_model():
    """Test that transcriber successfully loads a model."""
    transcriber = Transcriber()
    assert transcriber.load_model("tiny") is True
    assert transcriber.model is not None
```

## Submitting Changes

### Branching Strategy

- `main` - stable, production-ready code
- `develop` - integration branch for features (if needed)
- `feature/*` - new features
- `fix/*` - bug fixes
- `docs/*` - documentation updates

### Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise commit messages
   - Follow the coding standards
   - Add tests for new functionality

3. **Test your changes**
   ```bash
   pytest
   black .
   flake8 core ui app.py
   ```

4. **Update documentation**
   - Update README.md if needed
   - Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/)
   - Add docstrings to new functions/classes

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

6. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to GitHub and create a Pull Request
   - Fill in the PR template (if available)
   - Link related issues
   - Request review from maintainers

### Commit Message Format

Follow conventional commits format:

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: Add Excel rubric import functionality
fix: Resolve FFmpeg path issue on Windows
docs: Update installation instructions
```

## Release Process

Releases are managed by project maintainers. The process involves:

1. Update `__version__.py` with new version number
2. Update `CHANGELOG.md` with release notes
3. Create a git tag (e.g., `v1.0.0`)
4. Push tag to trigger CI/CD pipeline
5. GitHub Actions automatically builds and uploads release artifacts

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR version: Incompatible API changes
- MINOR version: New functionality (backwards-compatible)
- PATCH version: Bug fixes (backwards-compatible)

## Building Releases

### Building the Executable

```bash
python build.py
```

This creates:
- `dist/Transcribair.exe` - Standalone Windows executable
- Optimizations applied (UPX compression, symbol stripping)
- FFmpeg bundled automatically

### Building the Installer

Requires [Inno Setup](https://jrsoftware.org/isinfo.php):

1. Build the executable first: `python build.py`
2. Open `installer.iss` in Inno Setup Compiler
3. Click "Compile"
4. Installer created in `Output/` directory

## Getting Help

- **Documentation**: Check the [README](README.md) and [QUICKSTART](QUICKSTART.md)
- **Issues**: Search existing [GitHub Issues](https://github.com/otherworld-dev/TranscribAIr/issues)
- **Questions**: Open a new issue with the `question` label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to TranscribAIr! 🎉
