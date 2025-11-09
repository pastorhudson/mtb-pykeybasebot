#!/bin/bash
set -e

# Fix storage permissions on startup
if [ -d "/app/storage" ]; then
    echo "Fixing storage directory permissions..."
    chown -R appuser:appuser /app/storage
    chmod -R 755 /app/storage
fi

# Switch to appuser and run the command
exec gosu appuser "$@"