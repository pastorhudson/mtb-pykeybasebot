#!/bin/bash

# Install necessary system packages
apt-get update && apt-get install -y libgstreamer1.0-0 libwoff1 libgstreamer-plugins-base1.0-0 libgstreamer-gl1.0-0 libgstreamer-plugins-bad1.0-0 libflite1 libavif16 libenchant-2-2 libsecret-1-0 libhyphen0 libmanette-0.2-0 libgles2

# Exit if the installation fails
if [ $? -ne 0 ]; then
  echo "Failed to install dependencies"
  exit 1
fi

echo "Dependencies installed successfully"
