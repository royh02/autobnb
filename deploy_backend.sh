#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Step 1: Create and activate a virtual environment
VENV_DIR="venv"
echo "Creating virtual environment..."
python3 -m venv $VENV_DIR

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Step 2: Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Step 3: Clone a repository
REPO_URL="https://github.com/microsoft/autogen.git"
echo "Cloning repository from $REPO_URL..."
git clone $REPO_URL

# Step 4: Navigate to specific directories and install packages
echo "Changing directory to autogen/python..."
cd autogen/python

echo "Changing directory to packages/autogen-magentic-one and installing package..."
cd packages/autogen-magentic-one
pip install -e .

echo "Changing directory to packages/autogen-core and installing package..."
cd ../autogen-core
pip install -e .

echo "Changing directory to packages/autogen-ext and installing package..."
cd ../autogen-ext
pip install -e .

# Step 5: Return to the original directory and run the main script
echo "Returning to the original directory..."
cd ../../../..
echo "Running main.py..."
python main.py

echo "Setup complete!"