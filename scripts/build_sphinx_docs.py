#!/usr/bin/env python
"""
Build Sphinx documentation for PlanFlan

Usage:
    python build_sphinx_docs.py              # Build HTML
    python build_sphinx_docs.py clean        # Clean builds
    python build_sphinx_docs.py serve        # Build and serve
    python build_sphinx_docs.py strict       # Build with strict warnings
"""
import subprocess
import sys
import os
import shutil
import http.server
import socketserver

def build_docs(strict=False):
    """Build Sphinx documentation"""
    print("🔨 Generating Sphinx documentation...")
    print("-" * 80)
    
    cmd = ['sphinx-build', '-b', 'html', 'source', 'source/_build/html']
    if strict:
        cmd.insert(2, '-W')  # Treat warnings as errors
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("✅ Documentation generated successfully!")
        print(f"📁 Documentation available at: source/_build/html/")
        print("=" * 80)
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ Error generating documentation.")
        print("=" * 80)
        return False

def clean_docs():
    """Clean generated documentation"""
    print("🧹 Cleaning documentation build...")
    print("-" * 80)
    
    build_dir = '../source/_build'
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print("✅ Documentation cleaned successfully!")
    else:
        print("ℹ️  Nothing to clean (build directory doesn't exist)")

def serve_docs():
    """Build and serve documentation locally"""
    print("🚀 Building and serving documentation...")
    print("-" * 80)
    
    if not build_docs():
        return False
    
    os.chdir('../source/_build/html')
    
    print("\n🌐 Starting server on http://localhost:8000")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 80)
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            print(f"[{self.log_date_time_string()}] {format % args}")
    
    try:
        with socketserver.TCPServer(("", 8000), MyHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped.")
    finally:
        os.chdir('../../../..')

def main():
    """Main entry point"""
    print("=" * 80)
    print("  Sphinx Documentation Builder - PlanFlan")
    print("=" * 80)
    
    action = sys.argv[1] if len(sys.argv) > 1 else 'build'
    
    if action == 'clean':
        clean_docs()
    elif action == 'serve':
        serve_docs()
    elif action == 'strict':
        success = build_docs(strict=True)
        sys.exit(0 if success else 1)
    elif action == 'build' or action == '-h' or action == '--help':
        if action in ['-h', '--help']:
            print(__doc__)
            return
        success = build_docs()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown action: {action}")
        print(__doc__)
        sys.exit(1)

if __name__ == '__main__':
    main()
