#!/bin/bash

# Install necessary system packages
sudo apt-get update && sudo apt-get install -y libx11-xcb1 libxcursor1 libgtk-3-0

# Exit if the installation fails
if [ $? -ne 0 ]; then
  echo "Failed to install dependencies"
  exit 1
fi

echo "Dependencies installed successfully"
