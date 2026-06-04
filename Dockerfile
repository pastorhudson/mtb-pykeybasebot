FROM python:3.13-slim
#Install Deno for yt-dlp
COPY --from=denoland/deno:bin-2.5.6 /deno /usr/local/bin/deno

# Install system dependencies including ffmpeg, PostgreSQL client library, and gosu
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    ffmpeg \
    libpq-dev \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy the patched Go file before the build stage
COPY preview_dummy.go /tmp/preview_dummy.go

# Build patched Keybase with Linux audio waveform support
RUN apt-get update && apt-get install -y golang-go git && \
    cd /tmp && \
    git clone --depth=1 --filter=blob:none --sparse \
        https://github.com/keybase/client.git kb-src && \
    cd kb-src && \
    git sparse-checkout set go/ && \
    git checkout && \
    cp /tmp/preview_dummy.go go/chat/attachments/preview_dummy.go && \
    cd go/keybase && \
    go build -o /usr/local/bin/keybase . && \
    chmod +x /usr/local/bin/keybase && \
    cd / && \
    rm -rf /tmp/kb-src /tmp/preview_dummy.go && \
    apt-get remove -y golang-go git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/go /root/.cache/go-build && \
    echo "-----> Patched Keybase built successfully" && \
    keybase -v

# Add Keybase to PATH explicitly
ENV PATH="/usr/local/bin:${PATH}"

# Create a non-root user to run the app
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

ENV HOME=/app
WORKDIR /app

# Copy dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./

# Install uv and Python dependencies
RUN pip install --no-cache-dir uv && \
    uv sync --frozen

#Install Camoufox
ENV CAMOUFOX_CACHE_DIR=/app/.camoufox

RUN uv run python -m camoufox fetch && \
    chown -R appuser:appuser /app/.cache/camoufox && \
    chmod -R 755 /app/.cache/camoufox && \
    find /app/.venv/lib/python3.13/site-packages/camoufox/ -type d -exec chmod 755 {} \; && \
    find /app/.venv/lib/python3.13/site-packages/camoufox/ -type f -exec chmod 644 {} \; && \
    rm -rf /app/.venv/lib/python3.13/site-packages/camoufox/__pycache__

# Verify ffmpeg is available
RUN ffmpeg -version

# Copy application code and set ownership
COPY --chown=appuser:appuser . .

# Copy and set up entrypoint
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Create storage directory (will be overridden by Dokku mount, but good for local dev)
RUN mkdir -p /app/storage && \
    chown -R appuser:appuser /app/storage

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]