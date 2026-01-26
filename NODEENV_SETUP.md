# Installing Node.js in Virtual Environment with nodeenv

## Quick Setup

### Step 1: Install nodeenv (if not already installed)

```bash
pip install nodeenv
```

### Step 2: Create Node.js Environment in .venv

```bash
# Navigate to .venv directory
cd .venv

# Install Node.js in the virtual environment
nodeenv -p

# This installs Node.js in the current virtual environment
```

### Step 3: Verify Installation

```bash
# Check Node.js
node --version

# Check npm
npm --version
```

Both should show version numbers.

### Step 4: Install JSDoc in Virtual Environment

```bash
npm install -g jsdoc
```

Or better, add to requirements-dev.txt:

```
nodeenv>=1.8.0
```

### Step 5: Build Documentation

```bash
python build_sphinx_docs.py
```

---

## Complete Setup Script

Run these commands in order:

```bash
# 1. Activate your virtual environment
.\.venv\Scripts\activate

# 2. Install nodeenv
pip install nodeenv

# 3. Install Node.js in venv
nodeenv -p

# 4. Verify installations
node --version
npm --version
pip list | grep nodeenv

# 5. Install JSDoc
npm install -g jsdoc
jsdoc --version

# 6. Build documentation
python build_sphinx_docs.py
```

---

## If You Get Errors

### Error: "nodeenv is not recognized"
Make sure you're in the virtual environment:
```bash
.\.venv\Scripts\activate
pip install nodeenv
```

### Error: "nodeenv: command not found"
Reinstall nodeenv:
```bash
pip install --upgrade nodeenv
```

### Error: Node.js still not found
Try full path:
```bash
.\.venv\Scripts\node --version
.\.venv\Scripts\npm --version
```

---

## Verification Checklist

After setup, verify everything works:

```bash
# 1. Check Node.js in venv
node --version
# Should show: v20.x.x or similar

# 2. Check npm
npm --version
# Should show: 10.x.x or similar

# 3. Check JSDoc
jsdoc --version
# Should show: 4.x.x or similar

# 4. List Node packages
npm list -g jsdoc
# Should show JSDoc is installed

# 5. Build docs
python build_sphinx_docs.py
# Should complete with: ✅ Documentation generated successfully!
```

---

## What This Does

nodeenv allows you to:
- ✅ Keep Node.js isolated in your project
- ✅ Avoid system-wide Node.js installation
- ✅ Use Node.js only for this project
- ✅ Easy cleanup (just delete .venv)
- ✅ Share setup with team via requirements-dev.txt

---

## Recommended: Add to requirements-dev.txt

Add this line to `requirements-dev.txt`:

```
nodeenv>=1.8.0
```

Then others can install with:
```bash
pip install -r requirements-dev.txt
nodeenv -p
npm install -g jsdoc
```

---

## Quick Commands

```bash
# Activate venv and setup Node.js
.\.venv\Scripts\activate && pip install nodeenv && nodeenv -p

# Install JSDoc
npm install -g jsdoc

# Build documentation
python build_sphinx_docs.py

# Serve documentation
python build_sphinx_docs.py serve
```

---

**Done!** Your virtual environment now has Node.js and JSDoc isolated within it.
