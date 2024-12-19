#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Step 1: Create and activate a virtual environment
VENV_DIR="venv"
echo "Creating virtual environment..."
python3 -m venv $VENV_DIR

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Step 2: Install backend dependencies
echo "Installing backend dependencies from requirements.txt..."
pip install -r requirements.txt

# Step 3: Clone and install additional backend dependencies
rm -rf autogen
REPO_URL="https://github.com/microsoft/autogen.git"
echo "Cloning repository from $REPO_URL..."
git clone $REPO_URL

cd autogen/python/packages/autogen-magentic-one
pip install -e .
cd ../autogen-core
pip install -e .
cd ../autogen-ext
pip install -e .
cd ../../../..

# Step 4: Build the React frontend
echo "Building React frontend..."
cd autobnb-app
npm install
npm run build

# Step 5: Copy React build files to Flask's static directory
echo "Copying React build files to Flask's static directory..."
rm -rf ../static/build
mkdir -p ../static/build
cp -r build/* ../static/build

cd ..

echo "Build complete!"
