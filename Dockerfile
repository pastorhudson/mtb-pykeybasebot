FROM python:3.13-slim

# Install system dependencies including ffmpeg and PostgreSQL client library
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

# Create a non-root user to run the app
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

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

# Copy application code and set ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Procfile will handle the actual commands
CMD ["bash"]