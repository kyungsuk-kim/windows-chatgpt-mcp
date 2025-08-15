# Distribution Guide

This document explains how to build and distribute the Windows ChatGPT MCP Tool.

## Building Packages

### Prerequisites

1. Python 3.8 or higher
2. pip and setuptools installed
3. Windows 11 development environment

### Quick Build

Use the automated build script:

```bash
python build_dist.py
```

This will create both wheel packages and standalone executables.

### Manual Build Process

#### 1. Build Wheel Package

```bash
# Install build dependencies
pip install build wheel

# Clean previous builds
rm -rf build dist *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/windows_chatgpt_mcp-1.0.0-py3-none-any.whl` (wheel package)
- `dist/windows-chatgpt-mcp-1.0.0.tar.gz` (source distribution)

#### 2. Build Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller windows-chatgpt-mcp.spec
```

This creates:
- `dist/windows-chatgpt-mcp.exe` (standalone executable)

## Installation Methods

### Method 1: Pip Installation (Recommended)

```bash
pip install dist/windows_chatgpt_mcp-1.0.0-py3-none-any.whl
```

### Method 2: Standalone Executable

1. Download `windows-chatgpt-mcp.exe`
2. Place in desired directory
3. Run directly without Python installation

### Method 3: Development Installation

```bash
pip install -e .
```

## Distribution Checklist

- [ ] Version number updated in `setup.py` and `src/__version__.py`
- [ ] README.md updated with latest features
- [ ] CHANGELOG.md updated with release notes
- [ ] All tests passing
- [ ] Documentation updated
- [ ] License file included
- [ ] Requirements.txt up to date
- [ ] Build scripts tested
- [ ] Standalone executable tested on clean Windows system

## Package Contents

### Wheel Package Includes:
- Source code (`src/` directory)
- Documentation files
- Example configurations
- License and metadata

### Standalone Executable Includes:
- Compiled Python application
- All dependencies bundled
- Documentation files
- Example configurations
- No Python installation required

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH (e.g., 1.0.0)
- Update version in both `setup.py` and `src/__version__.py`

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Build packages using `python build_dist.py`
5. Test installations on clean systems
6. Create GitHub release with built packages
7. Upload to PyPI (if applicable)

## Troubleshooting Build Issues

### Common Issues:

1. **Missing dependencies**: Install build requirements
2. **PyInstaller errors**: Check hidden imports in spec file
3. **Path issues**: Ensure all data files are included in MANIFEST.in
4. **Windows-specific modules**: Verify pywin32 installation

### Debug Commands:

```bash
# Verbose build
python -m build --verbose

# PyInstaller debug
pyinstaller --debug=all windows-chatgpt-mcp.spec

# Test wheel installation
pip install --force-reinstall dist/windows_chatgpt_mcp-1.0.0-py3-none-any.whl
```