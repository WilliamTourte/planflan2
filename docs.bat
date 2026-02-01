@echo off
REM Quick batch file to call the Python documentation builder
REM This avoids issues with Make on Windows

python build_sphinx_docs.py %*
