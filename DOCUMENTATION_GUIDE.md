# Documentation Guide - PlanFlan

This guide explains how to build, maintain, and improve the documentation for the PlanFlan project.

## Quick Start

### Building Documentation Locally

#### Using Make (Recommended)
```bash
# Build documentation
make docs

# Clean old documentation
make docs-clean

# Build and serve documentation on http://localhost:8000
make docs-serve

# Build with strict warnings (fail on warnings)
make docs-strict
```

#### Using Direct Commands
```bash
# Navigate to source directory
cd source

# Build HTML documentation
sphinx-build -b html . _build/html

# Build with warnings treated as errors
sphinx-build -W -b html . _build/html

# Generate PDF documentation (requires LaTeX)
sphinx-build -b latex . _build/latex
cd _build/latex
make
```

### Viewing Documentation

After building with `make docs`, open `source/_build/html/index.html` in your web browser.

Or use the development server:
```bash
make docs-serve
# Then visit http://localhost:8000
```

---

## Documentation Structure

```
source/
├── conf.py                      # Sphinx configuration (settings, extensions, theme)
├── index.rst                    # Main documentation index page
├── modules.rst                  # Python modules auto-documentation
├── routes.rst                   # Flask routes documentation
├── routes/                      # Individual route documentation
│   ├── main.rst
│   ├── auth.rst
│   ├── photos.rst
│   └── maps.rst
├── templates.rst                # Template documentation
├── javascript.rst               # Manual JavaScript reference
├── javascript_autogen.rst       # Auto-generated JavaScript API docs
├── _templates/                  # Custom Sphinx templates
├── _static/                     # Static files (CSS, images)
└── _build/                      # Generated documentation output
    └── html/                    # HTML output
        ├── index.html
        └── ...
```

---

## Python Documentation

### Autodoc Configuration

Python source code is automatically documented using `sphinx.ext.autodoc`. The configuration is in `source/conf.py`:

```python
autodoc_default_options = {
    "members": True,              # Include all members (functions, classes)
    "undoc-members": False,       # Only documented items (requires docstrings)
    "private-members": False,     # Skip private functions (prefix with _)
    "special-members": "__init__", # Include constructors
    "show-inheritance": True,     # Show class inheritance
}
```

### Docstring Format

Python code uses Google-style docstrings (parsed by `sphinx.ext.napoleon`):

```python
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the distance between two geographical points.
    
    Uses the Haversine formula to compute the great-circle distance
    between two points on Earth given their latitudes and longitudes.
    
    Args:
        lat1: Starting latitude in decimal degrees
        lon1: Starting longitude in decimal degrees
        lat2: Ending latitude in decimal degrees
        lon2: Ending longitude in decimal degrees
    
    Returns:
        Distance in kilometers
    
    Raises:
        ValueError: If coordinates are outside valid ranges
    
    Example:
        >>> dist = calculate_distance(48.8566, 2.3522, 51.5074, -0.1278)
        >>> print(f"{dist:.2f} km")
        343.67 km
    """
```

### Best Practices

1. **Write comprehensive docstrings** - Every public function and class should have one
2. **Document parameters** - Include type information and descriptions
3. **Document return values** - Explain what the function returns
4. **Add examples** - Show typical usage in the docstring
5. **Mention exceptions** - Document errors that might be raised
6. **Keep it current** - Update docstrings when code changes

---

## JavaScript Documentation

### JSDoc Format

JavaScript files use standard JSDoc comments (parsed by `sphinx-js`):

```javascript
/**
 * Initialize the Google Maps with custom markers.
 * 
 * This function sets up the map with markers for all establishments
 * and enables real-time filtering based on user preferences.
 * 
 * @function initMap
 * @param {Object} mapContainer - The DOM element to mount the map
 * @param {string} mapContainer.id - Element ID
 * @param {Array<Object>} establishments - Array of establishment data
 * @param {number} establishments[].lat - Latitude
 * @param {number} establishments[].lng - Longitude
 * @returns {Promise<void>} Resolves when map is fully initialized
 * 
 * @throws {Error} If map API keys are missing
 * 
 * @example
 * // Initialize map with establishments
 * const container = document.getElementById('map');
 * const establishments = await fetchEstablishments();
 * await initMap(container, establishments);
 */
export async function initMap(mapContainer, establishments) {
    // Implementation
}
```

### Supported JSDoc Tags

- `@function` - Function name
- `@param {type} name` - Parameter with type
- `@returns {type}` - Return type and description
- `@throws {type}` - Possible exceptions
- `@example` - Usage examples
- `@deprecated` - Mark as deprecated
- `@async` - Async function
- `@class` - Class documentation
- `@constructor` - Constructor documentation
- `@property {type} name` - Class property

### JavaScript Best Practices

1. **Document exported functions** - All public functions should have JSDoc
2. **Include parameter types** - Help IDE autocomplete and documentation
3. **Provide examples** - Show practical usage
4. **Document classes** - Include `@class` and property descriptions
5. **Keep comments current** - Update when code changes

---

## Intersphinx Cross-References

The documentation can link to external project documentation. Configured projects:

- **Python**: https://docs.python.org/3
- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Werkzeug**: https://werkzeug.palletsprojects.com/
- **Jinja**: https://jinja.palletsprojects.com/

### Usage

```rst
:class:`flask.Flask` - Links to Flask.Flask class
:func:`datetime.now` - Links to datetime.now function
:mod:`flask.blueprints` - Links to Flask blueprints module
```

---

## Building Documentation in CI/CD

The GitHub Actions workflow `.github/workflows/documentation.yml` automatically:

1. **Builds documentation** on every push to `dev` or `main`
2. **Checks for warnings** - Reports documentation issues
3. **Uploads artifacts** - Saves HTML for review in PRs
4. **Deploys to GitHub Pages** - On main branch (requires setup)
5. **Comments on PRs** - Links to built documentation

### GitHub Pages Deployment

To enable automatic deployment to GitHub Pages:

1. Update `cname` in `.github/workflows/documentation.yml` with your domain
2. Enable GitHub Pages in repository settings
3. Select "Deploy from a branch" and set to `gh-pages` branch
4. Configure your custom domain (optional)

---

## Documentation Themes and Styling

### Theme: Read the Docs (sphinx_rtd_theme)

The documentation uses the professional Read the Docs theme with customization:

```python
# In conf.py
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,      # Show 4 levels in sidebar
    "collapse_navigation": False, # Keep all sections expanded
}
```

### Customization

Create custom styles in `source/_static/custom.css` and reference in `source/_templates/layout.html`.

---

## Common Tasks

### Adding a New Module Documentation

1. Create `source/mymodule.rst`:
```rst
mymodule
========

.. automodule:: mymodule
   :members:
   :undoc-members:
   :show-inheritance:
```

2. Add to `source/index.rst` toctree

3. Run `make docs` to build

### Adding a New JavaScript File Documentation

1. Add JSDoc comments to your JavaScript file
2. Update `source/javascript_autogen.rst` with a new section:
```rst
Module Name
-----------

.. js:autosummary::
   :maxdepth: 2

   mymodule
```

3. Run `make docs` to build

### Fixing Documentation Warnings

When building with `make docs-strict`:

1. **Undefined reference**: Check cross-reference syntax
   - Use `:class:`, `:func:`, `:mod:` for correct roles
   
2. **Missing title underline**: Ensure title has proper RST formatting
   
3. **Broken image**: Verify image paths exist
   
4. **Indentation errors**: Check RST list and code block indentation

---

## Troubleshooting

### Documentation won't build

**Check for errors:**
```bash
cd source
sphinx-build -b html . _build/html
```

**Common issues:**
- Missing `.rst` files referenced in toctree
- Python import errors (check `sys.path` in `conf.py`)
- Invalid RST syntax (check indentation)

### JSDoc not appearing

1. Verify file paths in `conf.py`: `js_source_path = "../app/static/js"`
2. Check JSDoc comment format (/** ... */)
3. Ensure `sphinx_js` is installed: `pip install sphinx-js`
4. Run `make docs-strict` to see warnings

### Theme not applying

```bash
# Clear old build
make docs-clean

# Rebuild
make docs
```

---

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [JSDoc Documentation](https://jsdoc.app/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)

---

## Contributing to Documentation

When submitting code:

1. **Write docstrings** for all public functions and classes
2. **Add examples** for complex functionality
3. **Update** docstrings when code changes
4. **Test builds** locally with `make docs-strict`
5. **Check** for warnings before committing

---

**Last Updated**: 2026-01-26  
**Maintainer**: Documentation Team  
**Status**: ✅ Production Ready
