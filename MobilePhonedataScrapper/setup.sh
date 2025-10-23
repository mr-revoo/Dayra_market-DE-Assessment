#!/bin/bash

# Mobile Phone Data Scraper - Setup and Run Script
# This script creates a virtual environment, installs dependencies, and runs the scraper

set -e  # Exit on error

echo "=========================================="
echo "Mobile Phone Data Scraper - Setup"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.11 or higher and try again."
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"
echo ""

# Check if virtual environment already exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " RECREATE
    if [[ "$RECREATE" =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf .venv
    else
        echo "Using existing virtual environment."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "  - selenium"
echo "  - beautifulsoup4"
echo "  - lxml"
echo "  - aiohttp"
echo "  - aiofiles"
echo "  - requests"
echo ""

pip install selenium beautifulsoup4 lxml aiohttp aiofiles requests -q

echo "✓ All dependencies installed"
echo ""

# Display installed packages
echo "Installed packages:"
pip list | grep -E "(selenium|beautifulsoup4|lxml|aiohttp|aiofiles|requests)"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Starting the scraper..."
echo ""

# Run the main scraper
python main.py

# Deactivate virtual environment on exit
deactivate 2>/dev/null || true

echo ""
echo "=========================================="
echo "Script finished."
echo "=========================================="
