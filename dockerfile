FROM python:3.13-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN curl --remote-name https://prerelease.keybase.io/keybase_amd64.deb \
    && apt install ./keybase_amd64.deb && rm keybase_amd64.deb

WORKDIR /app

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install uv and Python dependencies
RUN pip install --no-cache-dir uv && \
    uv sync --frozen

# Install Playwright browsers with dependencies (cached in layer)
RUN uv run playwright install --with-deps chromium

# Verify ffmpeg is available
RUN ffmpeg -version

# Copy application code
COPY . .

# Default command (override in app.json for different process types)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]