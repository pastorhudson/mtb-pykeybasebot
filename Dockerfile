FROM python:3.13-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    ffmpeg \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Keybase
RUN mkdir -p /usr/local/bin && \
    cd /tmp && \
    curl -sS --remote-name https://prerelease.keybase.io/keybase_amd64.deb && \
    dpkg-deb --fsys-tarfile keybase_amd64.deb | tar -xvf - --strip-components=3 ./usr/bin/keybase && \
    mv keybase /usr/local/bin/ && \
    chmod +x /usr/local/bin/keybase && \
    rm -f keybase_amd64.deb && \
    echo "-----> Keybase installed successfully" && \
    echo "-----> Keybase version:" && \
    keybase -v

# Add Keybase to PATH explicitly
ENV PATH="/usr/local/bin:${PATH}"

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
CMD ["bash"]
