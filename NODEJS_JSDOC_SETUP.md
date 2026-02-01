# Installing Node.js and JSDoc for JavaScript Documentation

## Quick Setup (Windows)

### Step 1: Install Node.js

1. **Download Node.js**
   - Visit: https://nodejs.org/
   - Download: **LTS version** (recommended)
   - File: `node-v20.x.x-x64.msi` or similar

2. **Install Node.js**
   - Run the installer
   - Click "Next" through the wizard
   - Accept default settings
   - Click "Install"
   - Click "Finish"

3. **Verify Installation**
   ```bash
   node --version
   npm --version
   ```
   Should show version numbers like `v20.x.x` and `10.x.x`

### Step 2: Install JSDoc Globally

Open Command Prompt or PowerShell and run:

```bash
npm install -g jsdoc
```

Wait for installation to complete (~30 seconds).

### Step 3: Verify JSDoc Installation

```bash
jsdoc --version
```

Should show a version number like `4.x.x`

---

## Building Documentation After Installation

Once Node.js and JSDoc are installed, building documentation is simple:

```bash
# From project directory
python build_sphinx_docs.py

# Or serve locally
python build_sphinx_docs.py serve
```

---

## Troubleshooting Installation

### Issue: "npm: command not found"
- Node.js wasn't installed properly
- Solution: Reinstall Node.js from https://nodejs.org/
- Make sure to use LTS version

### Issue: Permission denied
- Run Command Prompt as Administrator
- Then run: `npm install -g jsdoc`

### Issue: "jsdoc not found after installation"
- Close and reopen Command Prompt
- Try again: `jsdoc --version`

### Issue: Still getting "node.cmd not found"
1. Verify Node.js is in PATH:
   ```bash
   where node
   where npm
   ```
   Should show paths like: `C:\Program Files\nodejs\node.exe`

2. If paths don't show:
   - Reinstall Node.js
   - Make sure "Add to PATH" is checked

3. If still failing:
   - Add Node.js to PATH manually:
     - Open System Properties → Environment Variables
     - Add: `C:\Program Files\nodejs` to PATH

---

## Full Setup Checklist

After installation, verify everything:

```bash
# 1. Check Node.js
node --version
# Should show: v20.x.x or similar

# 2. Check npm
npm --version
# Should show: 10.x.x or similar

# 3. Check JSDoc
jsdoc --version
# Should show: 4.x.x or similar

# 4. Build documentation
cd C:\Users\dhugonnard2025\PycharmProjects\PythonProject\planflan3
python build_sphinx_docs.py
# Should show: ✅ Documentation generated successfully!
```

---

## What JSDoc Does

JSDoc allows Sphinx to automatically parse JavaScript comments like:

```javascript
/**
 * Initialize the map.
 * 
 * @param {Object} container - DOM element for map
 * @returns {Promise<void>} Resolves when ready
 * 
 * @example
 * await initMap(document.getElementById('map'));
 */
export async function initMap(container) {
    // ...
}
```

And automatically generates documentation from them!

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `node --version` | Check Node.js version |
| `npm --version` | Check npm version |
| `npm install -g jsdoc` | Install JSDoc globally |
| `jsdoc --version` | Check JSDoc version |
| `python build_sphinx_docs.py` | Build documentation |

---

## Alternative: Without Node.js (If Installation Fails)

If you can't install Node.js, you can still use the documentation:

1. **Edit** `source/conf.py`
2. **Remove** `"sphinx_js"` from extensions list
3. **Save** the file
4. **Run** `python build_sphinx_docs.py`

The JavaScript documentation will use the manual documentation in `javascript_autogen.rst` instead of auto-generating from JSDoc.

This is simpler but less automatic - you'll need to manually keep JavaScript docs in sync with code changes.

---

## Installation Time

- **Node.js**: 2-5 minutes
- **JSDoc**: 30 seconds
- **Total**: ~5-10 minutes

Then documentation building becomes fully automated!

---

**Next Step**: Install Node.js, then run:
```bash
python build_sphinx_docs.py
```

All set! 🚀
