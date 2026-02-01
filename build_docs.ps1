#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Build, clean, and serve Sphinx documentation for PlanFlan

.DESCRIPTION
    This PowerShell script provides cross-platform documentation building
    with support for clean, build, and serve operations.

.PARAMETER Action
    Action to perform: build (default), clean, or serve

.EXAMPLE
    .\build_docs.ps1               # Build documentation
    .\build_docs.ps1 clean         # Clean documentation
    .\build_docs.ps1 serve         # Build and serve on localhost:8000
    .\build_docs.ps1 strict        # Build with strict warnings

.NOTES
    Requires: Python 3.9+, Sphinx, sphinx-rtd-theme, sphinx-js
#>

param(
    [ValidateSet('build', 'clean', 'serve', 'strict')]
    [string]$Action = 'build'
)

$SourceDir = 'source'
$BuildDir = "$SourceDir\_build"
$HtmlDir = "$BuildDir\html"

function Build-Docs {
    Write-Host "🔨 Generating Sphinx documentation for PlanFlan..." -ForegroundColor Cyan
    
    Push-Location $SourceDir
    
    try {
        sphinx-build -b html . _build\html
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Documentation generated successfully!" -ForegroundColor Green
            Write-Host "📁 Documentation available at: $HtmlDir" -ForegroundColor Green
            Write-Host "🌐 Open source\_build\html\index.html in a browser to view." -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Error generating documentation." -ForegroundColor Red
            return $false
        }
    } finally {
        Pop-Location
    }
}

function Clean-Docs {
    Write-Host "🧹 Cleaning documentation build..." -ForegroundColor Yellow
    
    if (Test-Path $BuildDir) {
        Remove-Item -Recurse -Force $BuildDir
        Write-Host "✅ Documentation cleaned successfully!" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Nothing to clean (build directory doesn't exist)" -ForegroundColor Yellow
    }
}

function Serve-Docs {
    Write-Host "🚀 Building and serving documentation..." -ForegroundColor Cyan
    
    Push-Location $SourceDir
    
    try {
        sphinx-build -b html . _build\html
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Documentation generated successfully!" -ForegroundColor Green
            
            Push-Location $HtmlDir
            Write-Host "🌐 Starting server on http://localhost:8000" -ForegroundColor Green
            Write-Host "📝 Press Ctrl+C to stop the server" -ForegroundColor Yellow
            
            python -m http.server 8000
            
            Pop-Location
        } else {
            Write-Host "❌ Error generating documentation." -ForegroundColor Red
        }
    } finally {
        Pop-Location
    }
}

function Build-Docs-Strict {
    Write-Host "🔍 Building documentation with strict warning checking..." -ForegroundColor Cyan
    
    Push-Location $SourceDir
    
    try {
        sphinx-build -W -b html . _build\html
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Documentation generated successfully with no warnings!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Warnings detected in documentation." -ForegroundColor Red
            Write-Host "⚠️  Fix the warnings shown above before committing." -ForegroundColor Yellow
            return $false
        }
    } finally {
        Pop-Location
    }
}

# Main execution
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Sphinx Documentation Builder" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

switch ($Action) {
    'clean' { Clean-Docs }
    'serve' { Serve-Docs }
    'strict' { Build-Docs-Strict }
    'build' { Build-Docs }
    default { Build-Docs }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
