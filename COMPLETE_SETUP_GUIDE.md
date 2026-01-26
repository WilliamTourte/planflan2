# Complete Setup Guide - Node.js in Virtual Environment

## ⚡ Quick Setup (3 commands)

```bash
# 1. Install nodeenv
pip install nodeenv

# 2. Install Node.js in venv
nodeenv -p

# 3. Install JSDoc
npm install -g jsdoc
```

Then build:
```bash
python build_sphinx_docs.py
```

---

## 📋 Step-by-Step Setup

### Step 1: Make sure virtual environment is activated

```bash
# On Windows Command Prompt
.\.venv\Scripts\activate

# On Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of your command line.

### Step 2: Install nodeenv

```bash
pip install nodeenv
```

Expected output:
```
Successfully installed nodeenv-1.x.x
```

### Step 3: Install Node.js in the virtual environment

```bash
nodeenv -p
```

This installs Node.js into your `.venv` directory. Takes about 1-2 minutes.

Expected output:
```
...
nodeenv: saving seed-libs...
nodeenv: installing npm...
nodeenv: Done.
```

### Step 4: Verify Node.js installation

```bash
node --version
npm --version
```

Expected output:
```
v20.x.x (or similar)
10.x.x (or similar)
```

### Step 5: Install JSDoc

```bash
npm install -g jsdoc
```

Expected output:
```
added X packages, and audited X packages
```

### Step 6: Verify JSDoc installation

```bash
jsdoc --version
```

Expected output:
```
4.x.x (or similar)
```

### Step 7: Build documentation

```bash
python build_sphinx_docs.py
```

Expected output:
```
🔨 Generating Sphinx documentation...
────────────────────────────────────────────────────────────────────────────
Running Sphinx v9.1.0
loading translations [fr]... done
[...build process...]
✅ Documentation generated successfully!
```

---

## 🤖 Automatic Setup (Batch File)

We created a setup script for you:

```bash
# Make sure venv is activated first
.\.venv\Scripts\activate

# Then run the setup script
setup_nodeenv.bat
```

This will:
- ✅ Install nodeenv
- ✅ Install Node.js in venv
- ✅ Verify Node.js
- ✅ Install JSDoc
- ✅ Verify JSDoc

---

## ✅ Complete Verification Checklist

After setup, run these commands to verify everything:

```bash
# 1. Check Python is working
python --version
# Expected: Python 3.13.x

# 2. Check Node.js
node --version
# Expected: v20.x.x or similar

# 3. Check npm
npm --version
# Expected: 10.x.x or similar

# 4. Check JSDoc
jsdoc --version
# Expected: 4.x.x or similar

# 5. List installed npm packages
npm list -g jsdoc
# Should show JSDoc is installed

# 6. Build documentation
python build_sphinx_docs.py
# Should complete with ✅ success
```

---

## 🚀 Using the Setup

After Node.js is installed, building documentation is simple:

```bash
# Build (takes ~30 seconds)
python build_sphinx_docs.py

# Serve locally (auto-open http://localhost:8000)
python build_sphinx_docs.py serve

# Clean old builds
python build_sphinx_docs.py clean

# Check for issues
python build_sphinx_docs.py strict
```

---

## 📦 What Gets Installed

### In `.venv/Scripts/`
- `node.exe` - Node.js runtime
- `npm.cmd` - Node package manager
- `npm-cli.js` - npm CLI

### Globally (in npm)
- `jsdoc` - JSDoc parser for JavaScript documentation

All isolated within your virtual environment!

---

## 🔍 Troubleshooting

### Issue: "nodeenv: command not found"

**Solution:**
```bash
# Make sure venv is activated
.\.venv\Scripts\activate

# Reinstall nodeenv
pip install --upgrade nodeenv

# Try again
nodeenv -p
```

### Issue: "npm: command not found" after nodeenv -p

**Solution:**
```bash
# Close and reopen Command Prompt/PowerShell

# Verify installation
.\.venv\Scripts\npm --version

# Try using full path
.\.venv\Scripts\node --version
```

### Issue: Still getting "node.cmd was not found"

**Solution:**
```bash
# Make sure npm is in venv
.\.venv\Scripts\npm list -g jsdoc

# Reinstall JSDoc
.\.venv\Scripts\npm install -g jsdoc

# Try building
python build_sphinx_docs.py
```

### Issue: Installation takes too long

This is normal! Node.js is large (~150MB). Let it complete.

---

## 💡 Benefits of This Approach

✅ **Isolated**: Node.js only in your project  
✅ **Clean**: No system-wide installation  
✅ **Portable**: Easy to share with team  
✅ **Safe**: Easy to remove (just delete .venv)  
✅ **Professional**: Standard Python practice  

---

## 🔄 Team Setup

To set up for your team:

1. **Commit updated `requirements-dev.txt`**:
   ```bash
   git add requirements-dev.txt
   git commit -m "docs: add nodeenv for JSDoc support"
   ```

2. **Team members run:**
   ```bash
   pip install -r requirements-dev.txt
   nodeenv -p
   npm install -g jsdoc
   ```

   Or use the setup script:
   ```bash
   setup_nodeenv.bat
   ```

---

## 📝 Summary

After setup:

```bash
# Build documentation (one command!)
python build_sphinx_docs.py

# You now have:
# ✅ Python documentation (auto-generated)
# ✅ JavaScript documentation (auto-generated)
# ✅ Cross-references to Flask, SQLAlchemy, etc.
# ✅ Modern responsive theme
# ✅ CI/CD integration
# ✅ Full Windows support
```

**Total setup time**: ~5-10 minutes  
**Result**: Professional, automated documentation! 🎉

---

## Next Steps

1. Run the setup: `setup_nodeenv.bat`
2. Build documentation: `python build_sphinx_docs.py`
3. View locally: `python build_sphinx_docs.py serve`
4. Push to repository: `git commit -am "docs: complete sphinx setup"`

All done! ✨
