# Windows Documentation Build Guide

Since Windows doesn't have native `make` support, this guide shows the recommended ways to build documentation on Windows.

## ⭐ Recommended Method: Python Script

The simplest and most cross-platform way:

```bash
# Build documentation
python build_sphinx_docs.py

# View locally (starts server on http://localhost:8000)
python build_sphinx_docs.py serve

# Clean old builds
python build_sphinx_docs.py clean

# Build with strict warnings
python build_sphinx_docs.py strict
```

## Alternative 1: Batch File Wrapper

For even simpler commands:

```bash
# Build documentation
docs.bat

# View locally
docs.bat serve

# Clean
docs.bat clean

# Strict mode
docs.bat strict
```

## Alternative 2: Enhanced Batch File

For more control:

```bash
# Build documentation
build_docs.bat

# View locally (builds and serves)
build_docs.bat serve

# Clean
build_docs.bat clean

# Strict mode
build_docs.bat strict
```

## Alternative 3: PowerShell Script

If you prefer PowerShell:

```powershell
# Set execution policy if needed (one time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Build documentation
.\build_docs.ps1

# View locally
.\build_docs.ps1 serve

# Clean
.\build_docs.ps1 clean

# Strict mode
.\build_docs.ps1 strict
```

## Alternative 4: Direct Sphinx Commands

If you prefer command-line directly:

```bash
# Build HTML documentation
sphinx-build -b html source source/_build/html

# Build with strict warnings
sphinx-build -W -b html source source/_build/html

# View in browser
start source\_build\html\index.html

# Or serve locally
cd source\_build\html
python -m http.server 8000
```

## What Each Command Does

### Build
- Generates HTML documentation from RST source files
- Output: `source/_build/html/`
- Time: Usually 5-10 seconds

### Serve
- Builds documentation
- Starts local web server on http://localhost:8000
- Great for preview and development
- Press Ctrl+C to stop server

### Clean
- Deletes all generated documentation
- Useful when you have build issues
- Run before rebuild if having problems

### Strict
- Builds with `sphinx-build -W` flag
- Treats warnings as errors
- Ensures documentation quality
- Recommended before committing

## Troubleshooting

### "Command not found" on build_sphinx_docs.py

Make sure:
1. Python is installed and in PATH
2. You're in the project directory
3. The file exists: `ls build_sphinx_docs.py`

### "ModuleNotFoundError: No module named 'sphinx'"

Install dependencies:
```bash
pip install -r requirements-dev.txt
```

### "Address already in use" when serving

Another process is using port 8000:
```bash
# Try a different port
python -m http.server 8000 --directory source/_build/html
# Use port 8001 or 9000 if 8000 is busy
```

### Build fails with "conf.py error"

Check the source/conf.py file for syntax errors:
```bash
python -m py_compile source/conf.py
```

## Viewing Documentation

After building with `python build_sphinx_docs.py`:

1. **Open in browser directly:**
   ```
   source\_build\html\index.html
   ```

2. **Or use serve:**
   ```bash
   python build_sphinx_docs.py serve
   # Visit http://localhost:8000
   ```

3. **Or start HTTP server manually:**
   ```bash
   cd source\_build\html
   python -m http.server 8000
   # Visit http://localhost:8000
   ```

## Quick Reference

| Task | Command |
|------|---------|
| Build | `python build_sphinx_docs.py` |
| Build (strict) | `python build_sphinx_docs.py strict` |
| Serve locally | `python build_sphinx_docs.py serve` |
| Clean build | `python build_sphinx_docs.py clean` |
| View (manual) | `start source\_build\html\index.html` |

## Why Not `make docs`?

The `Makefile` is designed for Unix-like systems (Linux, macOS).

Windows alternatives:
- `nmake` - Requires Visual Studio
- Batch files - Windows native
- PowerShell - Modern Windows
- Python - Cross-platform best option

## Recommended Setup

For optimal Windows experience, add this to your PowerShell profile:

```powershell
# In your PowerShell profile (~\Documents\PowerShell\profile.ps1)
function docs-build { python build_sphinx_docs.py }
function docs-serve { python build_sphinx_docs.py serve }
function docs-clean { python build_sphinx_docs.py clean }
```

Then you can use:
```powershell
docs-build      # Build
docs-serve      # Serve
docs-clean      # Clean
```

## Integration with IDE

### Visual Studio Code

Add to `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build Documentation",
            "type": "shell",
            "command": "python",
            "args": ["build_sphinx_docs.py"],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        }
    ]
}
```

Then press `Ctrl+Shift+B` to build.

### PyCharm

1. Go to Run → Edit Configurations
2. Click +
3. Select Python
4. Set:
   - Script path: `build_sphinx_docs.py`
   - Parameters: (leave empty or add: `serve`)
5. Click OK
6. Click Run

## Summary

**Best option for Windows:** `python build_sphinx_docs.py`

- ✅ No dependencies (Python is required anyway)
- ✅ Cross-platform
- ✅ Full feature support
- ✅ Clear output and feedback
- ✅ Works with IDE integration

Use this command and you'll be all set!
