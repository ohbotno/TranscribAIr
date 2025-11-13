# TranscribAIr - Release Process Documentation

This document contains important information about the release process, CI/CD setup, and lessons learned from establishing the automated build workflow.

## Table of Contents

- [Quick Release Checklist](#quick-release-checklist)
- [Detailed Release Process](#detailed-release-process)
- [Version Numbering](#version-numbering)
- [CI/CD Workflow](#cicd-workflow)
- [Common Issues & Solutions](#common-issues--solutions)
- [Files to Update for Each Release](#files-to-update-for-each-release)
- [Testing Before Release](#testing-before-release)
- [Post-Release Checklist](#post-release-checklist)

---

## Quick Release Checklist

Use this for routine releases after the initial setup:

1. **Update version number** in all required files
2. **Update CHANGELOG.md** with changes
3. **Commit changes** with conventional commit message
4. **Create annotated tag** with release notes
5. **Push to GitHub** (commits then tag)
6. **Monitor CI/CD** workflow
7. **Test the release** artifact
8. **Announce release** (if applicable)

---

## Detailed Release Process

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

### Step 5: Push to GitHub

**Important:** Push commits FIRST, then tags:

```bash
# Push commits
git push origin main

# Push tag (triggers CI/CD)
git push origin vX.Y.Z
```

### Step 6: Monitor CI/CD

1. Go to: https://github.com/otherworld-dev/TranscribAIr/actions
2. Watch the workflow run
3. Expected duration: 5-10 minutes
4. Workflow should:
   - Set up Python 3.11
   - Install dependencies
   - Install FFmpeg automatically
   - Build optimized executable (~80-100MB)
   - Create portable ZIP
   - Create GitHub Release with artifacts

### Step 7: Verify Release

1. Check release page: https://github.com/otherworld-dev/TranscribAIr/releases
2. Download `TranscribAIr-X.Y.Z-Portable.zip`
3. Extract and test the executable
4. Verify all features work correctly

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

## CI/CD Workflow

### Workflow File Location
`.github/workflows/release.yml`

### Trigger
Workflow runs automatically when a tag matching `v*.*.*` is pushed:

```bash
git push origin v1.0.0  # Triggers workflow
git push origin main    # Does NOT trigger workflow
```

### Workflow Steps

1. **Checkout code** - Clones repository
2. **Set up Python 3.11** - Installs Python
3. **Get version from tag** - Extracts version number
4. **Install dependencies** - Runs `pip install -r requirements.txt` + PyInstaller
5. **Install FFmpeg** - Runs `python install_ffmpeg.py --auto`
6. **Build executable** - Runs `python build.py`
7. **Create portable ZIP** - Packages executable
8. **Upload artifacts** - Stores build outputs
9. **Create GitHub Release** - Publishes release with artifacts

### Environment Variables

```yaml
CI: 'true'                    # Auto-detected by scripts
GITHUB_ACTIONS: 'true'        # Auto-detected by scripts
PYTHONIOENCODING: 'utf-8'     # Set in workflow
```

These environment variables tell `install_ffmpeg.py` and `build.py` to:
- Skip interactive prompts
- Use ASCII output (no Unicode symbols)
- Auto-install dependencies

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
