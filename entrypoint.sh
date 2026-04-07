#!/bin/bash
set -e

# Fix storage permissions on startup
if [ -d "/app/storage" ]; then
    echo "Fixing storage directory permissions..."
    chown -R appuser:appuser /app/storage
    chmod -R 755 /app/storage
fi

# Fix camoufox permissions
if [ -d "/app/.venv/lib/python3.13/site-packages/camoufox" ]; then
    echo "Fixing camoufox permissions..."
    chmod -R 644 /app/.venv/lib/python3.13/site-packages/camoufox/
fi

# Switch to appuser and run the command
exec gosu appuser "$@"