#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

apt-get update && apt-get install -y \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2-mesa

# Activate virtual environment
VENV_DIR="venv"
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate
playwright install

# Run the Flask application
echo "Running Flask application..."
python main.py
echo "Deployment complete!"