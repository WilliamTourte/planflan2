#!/bin/bash
# Script to ensure proper coverage reporting
# Usage: ./scripts/ensure_coverage.sh [test_command]

# Clean up old coverage data
rm -f .coverage htmlcov/*

# Run the provided test command (or default to all tests)
if [ $# -eq 0 ]; then
    echo "Running all tests with coverage..."
    python -m pytest tests/ --cov=app --cov-report=html --cov-report=term --cov-report=xml -v
else
    echo "Running custom test command: $@"
    $@ --cov=app --cov-report=html --cov-report=term
fi

# Check if coverage was successful
if [ $? -eq 0 ]; then
    echo "✅ Tests passed!"
    
    # Generate HTML report if it doesn't exist
    if [ ! -f "htmlcov/index.html" ]; then
        echo "📊 Generating HTML coverage report..."
        coverage html
    fi
    
    # Generate XML report if it doesn't exist
    if [ ! -f "coverage.xml" ]; then
        echo "📊 Generating XML coverage report for CI..."
        coverage xml
    fi
    
    # Show summary
    echo "📈 Coverage Summary:"
    coverage report --show-missing
else
    echo "❌ Tests failed!"
    exit 1
fi