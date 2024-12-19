#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Step 1: Navigate to the frontend directory
echo "Changing directory to autobnb-app..."
cd autobnb-app

# Step 2: Install frontend dependencies
echo "Installing frontend dependencies with npm..."
npm install

# Step 3: Start the frontend application
echo "Starting the frontend application..."
npm run start

echo "Frontend deployment complete!"
