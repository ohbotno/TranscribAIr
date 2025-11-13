# TranscribAIr - Release Process Documentation

This document contains important information about the manual release process and version management.

## Table of Contents

- [Quick Release Checklist](#quick-release-checklist)
- [Manual Release Process](#manual-release-process)
- [Version Numbering](#version-numbering)
- [Building the Executable](#building-the-executable)
- [Creating GitHub Release](#creating-github-release)
- [Files to Update for Each Release](#files-to-update-for-each-release)
- [Testing Before Release](#testing-before-release)
- [Post-Release Checklist](#post-release-checklist)

---

## Note on Automated Releases

**Automated CI/CD releases were removed in v1.0.5** due to complexity and reliability issues. Releases are now created manually to ensure quality and proper testing before distribution.

---

## Quick Release Checklist

Use this for routine releases:

1. **Update version number** in all required files
2. **Update CHANGELOG.md** with changes
3. **Build and test executable** locally
4. **Commit changes** with conventional commit message
5. **Create Git tag** with release notes
6. **Create GitHub Release** manually
7. **Upload executable** to release
8. **Announce release** (if applicable)

---

## Manual Release Process

### Step 1: Update Version Numbers

Update the version in these files (use find & replace):

```bash
# Files to update for version X.Y.Z:
__version__.py          # Line 5: __version__ = "X.Y.Z"
README.md              # Line 3: Badge version
README.md              # Line 39: Installer filename
installer.iss          # Line 12: #define MyAppVersion "X.Y.Z"
```

**Example for version 1.1.0:**
- `__version__.py`: `__version__ = "1.1.0"`
- `README.md`: `[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)]`
- `README.md`: `Download TranscribAIr-1.1.0-Setup.exe`
- `installer.iss`: `#define MyAppVersion "1.1.0"`

### Step 2: Update CHANGELOG.md

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Features to be removed in future

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes
```

### Step 3: Commit Changes

Use conventional commit format:

```bash
# For new features (minor version bump)
git commit -m "feat: Add new feature description"

# For bug fixes (patch version bump)
git commit -m "fix: Fix bug description"

# For breaking changes (major version bump)
git commit -m "feat!: Breaking change description

BREAKING CHANGE: Description of what breaks"

# For releases
git commit -m "chore: Release version X.Y.Z

- Update version to X.Y.Z
- Update CHANGELOG with release notes"
```

### Step 4: Create Git Tag

Create an annotated tag (not lightweight):

```bash
git tag -a vX.Y.Z -m "TranscribAIr vX.Y.Z - Release Title

Brief description of this release.

Added:
- Feature 1
- Feature 2

Fixed:
- Bug fix 1
- Bug fix 2

See CHANGELOG.md for detailed changes."
```

### Step 5: Build the Executable

Build locally and test:

```bash
# Build the executable
python build.py

# This will create: dist/Transcribair.exe
```

Test the executable thoroughly:
- Launch and check UI
- Test transcription (upload and record)
- Test feedback organization
- Test export features
- Verify on clean Windows machine if possible

### Step 6: Create Git Tag

```bash
git tag -a vX.Y.Z -m "TranscribAIr vX.Y.Z - Release Title

Brief description of this release.

Added:
- Feature 1
- Feature 2

Fixed:
- Bug fix 1
- Bug fix 2

See CHANGELOG.md for detailed changes."
```

### Step 7: Push to GitHub

```bash
# Push commits
git push origin main

# Push tag
git push origin vX.Y.Z
```

### Step 8: Create GitHub Release

1. Go to: https://github.com/otherworld-dev/TranscribAIr/releases/new
2. Select the tag you just pushed
3. Release title: `TranscribAIr vX.Y.Z`
4. Copy release notes from CHANGELOG.md
5. Upload `dist/Transcribair.exe` (or create ZIP: `TranscribAIr-X.Y.Z-Portable.zip`)
6. Upload installer if created (from Inno Setup)
7. Publish release

---

## Version Numbering

Follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backwards-compatible
- **PATCH** (0.0.X): Bug fixes, backwards-compatible

**Examples:**
- `1.0.0` → `1.0.1`: Bug fix (patch)
- `1.0.0` → `1.1.0`: New feature (minor)
- `1.0.0` → `2.0.0`: Breaking change (major)

---

## Building the Executable

### Prerequisites

- Python 3.9-3.13 installed
- Virtual environment set up (via `setup.bat` or `setup.sh`)
- PyInstaller installed (`pip install pyinstaller`)
- FFmpeg available (auto-installed by build script)

### Build Process

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Build executable
python build.py
```

The build script will:
1. Check for PyInstaller
2. Install FFmpeg if needed
3. Update build.spec with FFmpeg binaries
4. Run PyInstaller with optimizations
5. Create `dist/Transcribair.exe` (~150-200MB)

### Build Optimizations

Current settings (in `build.spec`):
- **UPX compression**: Disabled (causes DLL issues)
- **Symbol stripping**: Disabled (better compatibility)
- **Package exclusions**: Enabled (removes unused packages)
- **FFmpeg**: Bundled in executable

### Creating Distribution ZIP

```bash
# Windows (PowerShell)
cd dist
Compress-Archive -Path Transcribair.exe -DestinationPath TranscribAIr-X.Y.Z-Portable.zip

# Linux/macOS
cd dist
zip TranscribAIr-X.Y.Z-Portable.zip Transcribair.exe
```

---

## Creating GitHub Release

### Manual Release Steps

1. **Build and test executable locally** (see above)
2. **Create ZIP file** for distribution
3. **Go to GitHub**:
   - Navigate to: https://github.com/otherworld-dev/TranscribAIr/releases/new
4. **Fill in release form**:
   - Choose tag: Select the tag you pushed (vX.Y.Z)
   - Release title: `TranscribAIr vX.Y.Z`
   - Description: Copy from CHANGELOG.md
5. **Upload artifacts**:
   - `TranscribAIr-X.Y.Z-Portable.zip` (required)
   - `TranscribAIr-X.Y.Z-Setup.exe` (optional, if using Inno Setup)
6. **Publish release**

### Release Notes Template

```markdown
## What's New

[Copy Added/Changed/Fixed sections from CHANGELOG.md]

## Installation

**For End Users:**
- Download `TranscribAIr-X.Y.Z-Portable.zip`
- Extract and run `Transcribair.exe`
- No installation required!

**For Developers:**
- Clone the repository
- See [README.md](README.md) for setup instructions

## System Requirements
- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB+ recommended)
- 500MB disk space + Whisper models (75MB-2.9GB)

## Links
- [Full Changelog](CHANGELOG.md)
- [Documentation](README.md)
- [Report Issues](https://github.com/otherworld-dev/TranscribAIr/issues)
```

---

## Common Issues & Solutions

### Issue 1: Interactive Prompts (v1.0.0 → v1.0.1)

**Problem:** Scripts prompted for user input in non-interactive CI environment.

**Error:**
```
EOFError: EOF when reading a line
```

**Solution:**
- Added CI environment detection in scripts
- Scripts check for `GITHUB_ACTIONS` or `CI` environment variables
- Auto-install mode enabled in CI
- Use `--auto` or `-y` flags when calling scripts

**Files Modified:**
- `install_ffmpeg.py` - Added auto-detect CI mode
- `build.py` - Added auto-detect CI mode

### Issue 2: Unicode Encoding (v1.0.1 → v1.0.2)

**Problem:** Windows GitHub Actions uses cp1252 encoding, can't handle Unicode symbols (✓, ✗).

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

**Solution:**
- Replaced all Unicode symbols with ASCII equivalents:
  - `✓` → `[OK]`
  - `✗` → `[ERROR]`
  - `⚠` → `[WARNING]`
- Added `PYTHONIOENCODING: 'utf-8'` to workflow

**Files Modified:**
- `install_ffmpeg.py` - All print statements
- `build.py` - All print statements
- `.github/workflows/release.yml` - Added env var

### Issue 3: Missing build.spec (v1.0.2 → v1.0.3)

**Problem:** `build.spec` was in `.gitignore` and not committed to repository.

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'build.spec'
```

**Solution:**
- Updated `.gitignore` to allow `build.spec`
- Force-added file with `git add -f build.spec`
- Commented out `*.spec` exclusion in `.gitignore`

**Files Modified:**
- `.gitignore` - Allowed spec files
- `build.spec` - Added to repository

---

## Files to Update for Each Release

### Required Updates

| File | What to Update | Example |
|------|----------------|---------|
| `__version__.py` | Line 5: Version string | `__version__ = "1.1.0"` |
| `CHANGELOG.md` | Add new version section at top | `## [1.1.0] - 2025-11-14` |
| `README.md` | Line 3: Version badge | `version-1.1.0-blue.svg` |
| `README.md` | Line 39: Installer filename | `TranscribAIr-1.1.0-Setup.exe` |
| `installer.iss` | Line 12: AppVersion | `#define MyAppVersion "1.1.0"` |

### Git Operations

```bash
# Stage all version-related files
git add __version__.py CHANGELOG.md README.md installer.iss

# Commit
git commit -m "chore: Release version X.Y.Z"

# Tag
git tag -a vX.Y.Z -m "Release notes here"

# Push (commits first, then tag)
git push origin main
git push origin vX.Y.Z
```

---

## Testing Before Release

### Local Build Test

Before creating a release, test the build locally:

```bash
# Ensure you're in the project root
cd TranscribAIr

# Run the build script
python build.py

# Check the output
# Expected: dist/Transcribair.exe (~80-100MB)
# Should see: [OK] Build successful!

# Test the executable
cd dist
./Transcribair.exe
```

### Pre-Release Checklist

- [ ] All tests pass (when tests are added)
- [ ] Version numbers updated in all files
- [ ] CHANGELOG.md updated with all changes
- [ ] Local build succeeds
- [ ] Executable runs and all features work
- [ ] No untracked files with sensitive data
- [ ] Commit message follows conventions
- [ ] Tag annotation includes release notes

---

## Post-Release Checklist

After CI/CD completes:

- [ ] Download and test the release artifact
- [ ] Verify release page looks correct
- [ ] Check release notes are properly formatted
- [ ] Test executable on clean Windows machine
- [ ] Update project documentation if needed
- [ ] Announce release (if applicable)
- [ ] Monitor for issues reported by users

---

## Build Optimization Settings

The build process includes these optimizations (configured in `build.spec`):

### Excluded Packages (saves ~40% size)
```python
excludes=[
    'matplotlib', 'scipy', 'pandas', 'torch', 'tensorflow',
    'pytest', 'unittest', 'IPython', 'jupyter', 'sphinx',
    'pydoc', 'pdb', 'asyncio', 'multiprocessing', 'xml.dom'
]
```

### Compression Settings
```python
strip=True              # Remove debug symbols
upx=True               # Enable UPX compression
upx_exclude=[          # Don't compress these (causes issues)
    'vcruntime140.dll',
    'python*.dll',
    'Qt*.dll',
]
```

### Result
- Unoptimized build: ~200MB
- Optimized build: ~80-100MB (50% reduction)

---

## Installer Creation (Optional/Manual)

To create a Windows installer using Inno Setup:

### Prerequisites
1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the executable first: `python build.py`

### Steps
1. Open `installer.iss` in Inno Setup Compiler
2. Click "Build" → "Compile"
3. Wait for compilation (~30 seconds)
4. Find installer in `Output/TranscribAIr-X.Y.Z-Setup.exe`

### Installer Features
- Installs to `C:\Program Files\TranscribAIr`
- Creates Start Menu shortcuts
- Optional desktop icon
- Proper uninstaller
- Preserves user data in `%USERPROFILE%\.transcribair`

**Note:** Installer creation is currently manual. Could be automated in CI/CD with Inno Setup CLI.

---

## GitHub Release Page

### Automatic Content

The release page automatically includes:
- Release title: `TranscribAIr vX.Y.Z`
- Tag name: `vX.Y.Z`
- Release notes from CHANGELOG.md
- Artifacts:
  - `TranscribAIr-X.Y.Z-Portable.zip` (built executable)
  - `Source code (zip)` (automatic)
  - `Source code (tar.gz)` (automatic)
- License, README, CHANGELOG files

### Release Notes Format

Release notes are extracted from CHANGELOG.md and combined with:
- Installation instructions
- System requirements
- Download links

See `.github/workflows/release.yml` for the extraction logic.

---

## Important Notes

### DO NOT

- ❌ Delete tags after pushing (breaks releases)
- ❌ Force-push to main after tagging
- ❌ Use lightweight tags (`git tag vX.Y.Z` without `-a`)
- ❌ Tag without updating version files
- ❌ Push tag before pushing commits
- ❌ Add Unicode symbols to scripts (breaks Windows CI)
- ❌ Add interactive prompts to build scripts

### DO

- ✅ Use annotated tags with messages
- ✅ Update all version files before tagging
- ✅ Test build locally before release
- ✅ Follow semantic versioning
- ✅ Keep CHANGELOG.md up to date
- ✅ Push commits before tags
- ✅ Use ASCII symbols in scripts ([OK], [ERROR])
- ✅ Add `--auto` flags for CI-compatible scripts

---

## Workflow Monitoring

### Check Workflow Status

```bash
# Via GitHub web interface
https://github.com/otherworld-dev/TranscribAIr/actions

# Via GitHub CLI (if installed)
gh run list
gh run view <run-id>
```

### Expected Workflow Duration

| Step | Duration |
|------|----------|
| Setup Python | ~30 seconds |
| Install dependencies | ~2-3 minutes |
| Install FFmpeg | ~1 minute (download 197MB) |
| Build executable | ~2-3 minutes |
| Create release | ~30 seconds |
| **Total** | **~5-10 minutes** |

### Workflow Success Indicators

Look for these in the logs:
- `[OK] PyInstaller found`
- `[OK] FFmpeg installed successfully!`
- `[OK] Build successful!`
- `Size: XX.XX MB`
- `Release v1.X.X created successfully!`

---

## Troubleshooting

### Build Fails: "No module named 'X'"

**Cause:** Missing dependency in `requirements.txt`

**Solution:** Add missing package to `requirements.txt` and retry

### Build Fails: "Permission denied"

**Cause:** Previous build artifacts exist

**Solution:** Clean build directories (automatic in workflow with `--clean`)

### Executable Crashes on Launch

**Possible causes:**
1. Missing hidden imports in `build.spec`
2. DLL compatibility issues
3. Python version mismatch

**Solution:**
- Add missing modules to `hiddenimports` in `build.spec`
- Test on clean Windows machine
- Rebuild with matching Python version

### Release Artifact Missing

**Cause:** Build step failed silently

**Solution:** Check workflow logs for actual error, may need to scroll up past verbose output

---

## Future Improvements

### Planned Enhancements

1. **Automated installer build** - Add Inno Setup to CI/CD
2. **Code signing** - Sign executable with certificate
3. **Multi-platform builds** - Linux AppImage, macOS .app
4. **Automated testing** - Add pytest to CI/CD
5. **Version auto-increment** - Script to bump versions
6. **Release notes automation** - Generate from commits
7. **Changelog validation** - Ensure CHANGELOG is updated

### Ideas to Consider

- GitHub Actions workflow for pull requests (build but don't release)
- Nightly builds from main branch
- Beta/pre-release channels
- Download statistics tracking
- Auto-update mechanism in app

---

## Contact & Support

- **Repository:** https://github.com/otherworld-dev/TranscribAIr
- **Issues:** https://github.com/otherworld-dev/TranscribAIr/issues
- **Releases:** https://github.com/otherworld-dev/TranscribAIr/releases

---

## Version History

| Version | Date | Issues Fixed | Notes |
|---------|------|--------------|-------|
| v1.0.0 | 2025-11-13 | - | Initial release, CI failed (prompts) |
| v1.0.1 | 2025-11-13 | Interactive prompts | CI failed (Unicode) |
| v1.0.2 | 2025-11-13 | Unicode encoding | CI failed (missing spec) |
| v1.0.3 | 2025-11-13 | Missing build.spec | ✅ First successful automated build |

---

*Last updated: 2025-11-13*
*Next review: Before v1.1.0 release*
