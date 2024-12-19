#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Activate virtual environment
VENV_DIR="venv"
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Run the Flask application
echo "Running Flask application..."
python main.py
echo "Deployment complete!"