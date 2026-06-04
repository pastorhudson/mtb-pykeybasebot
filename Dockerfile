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

# Build patched Keybase with Linux audio waveform support
# Uses a multi-stage-style approach: install Go, build, remove Go
RUN apt-get update && apt-get install -y golang-go git && \
    \
    # Clone only the Go source (sparse, shallow)
    cd /tmp && \
    git clone --depth=1 --filter=blob:none --sparse \
        https://github.com/keybase/client.git kb-src && \
    cd kb-src && \
    git sparse-checkout set go/ && \
    git checkout && \
    \
    # Patch preview_dummy.go to add Linux audio waveform support via ffmpeg
    cat > go/chat/attachments/preview_dummy.go << 'GOEOF'
//go:build !darwin && !android
// +build !darwin,!android

package attachments

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/keybase/client/go/chat/types"
	"github.com/keybase/client/go/chat/utils"
)

const audioAmpsCount = 60

func isAudioExtension(basename string) bool {
	switch strings.ToLower(filepath.Ext(basename)) {
	case ".m4a", ".mp3", ".aac", ".ogg", ".flac", ".wav", ".opus", ".aiff", ".caf", ".mp4":
		return true
	}
	return false
}

func normalizeAudioAmps(amps []float64) []float64 {
	if len(amps) == 0 {
		return make([]float64, audioAmpsCount)
	}
	return amps
}

func getAudioAmpsLinux(basename string) ([]float64, int) {
	probeOut, err := exec.Command("ffprobe",
		"-v", "quiet",
		"-print_format", "json",
		"-show_streams",
		basename,
	).Output()
	durationMs := 0
	if err == nil {
		var probeResult struct {
			Streams []struct {
				Duration  string `json:"duration"`
				CodecType string `json:"codec_type"`
			} `json:"streams"`
		}
		if json.Unmarshal(probeOut, &probeResult) == nil {
			for _, s := range probeResult.Streams {
				if s.CodecType == "audio" {
					var dur float64
					if _, err := fmt.Sscanf(s.Duration, "%f", &dur); err == nil {
						durationMs = int(dur * 1000)
					}
					break
				}
			}
		}
	}

	pcmData, err := exec.Command("ffmpeg",
		"-i", basename,
		"-ac", "1",
		"-ar", "8000",
		"-f", "s16le",
		"-",
	).Output()
	if err != nil || len(pcmData) < 2 {
		return nil, durationMs
	}

	numSamples := len(pcmData) / 2
	bucketSize := numSamples / audioAmpsCount
	if bucketSize < 1 {
		bucketSize = 1
	}
	amps := make([]float64, audioAmpsCount)
	for i := 0; i < audioAmpsCount; i++ {
		start := i * bucketSize
		end := start + bucketSize
		if end > numSamples {
			end = numSamples
		}
		var sumSq float64
		count := end - start
		for j := start; j < end; j++ {
			lo := pcmData[j*2]
			hi := pcmData[j*2+1]
			sample := float64(int16(uint16(lo) | uint16(hi)<<8))
			sumSq += sample * sample
		}
		rms := math.Sqrt(sumSq / float64(count))
		amps[i] = rms / 32768.0
	}
	return amps, durationMs
}

func previewAudio(duration int, amps []float64) (*PreviewRes, error) {
	amps = normalizeAudioAmps(amps)
	dbAmps := make([]float64, len(amps))
	for i, a := range amps {
		if a <= 0 {
			dbAmps[i] = -80
		} else {
			dbAmps[i] = 20 * math.Log10(a)
		}
	}
	v := newAudioVisualizer(dbAmps)
	dat, width := v.visualize()
	return &PreviewRes{
		Source:         dat,
		ContentType:    "image/png",
		BaseWidth:      width,
		BaseHeight:     v.height,
		BaseDurationMs: duration,
		BaseIsAudio:    true,
		AudioAmps:      amps,
		PreviewWidth:   width,
		PreviewHeight:  v.height,
	}, nil
}

func previewVideo(ctx context.Context, log utils.DebugLabeler, src io.Reader,
	basename string, nvh types.NativeVideoHelper,
) (*PreviewRes, error) {
	if isAudioExtension(basename) {
		amps, duration := getAudioAmpsLinux(basename)
		if duration > 0 {
			return previewAudio(duration, amps)
		}
	}
	return previewVideoBlank(ctx, log, src, basename)
}

func HEICToJPEG(ctx context.Context, log utils.DebugLabeler, basename string) (dat []byte, err error) {
	return nil, nil
}
GOEOF
    \
    # Build the patched binary
    cd /tmp/kb-src/go/keybase && \
    go build -o /usr/local/bin/keybase . && \
    chmod +x /usr/local/bin/keybase && \
    \
    # Clean up — remove Go, source, and build cache to keep image small
    cd / && \
    rm -rf /tmp/kb-src && \
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

# Stay as root for entrypoint to fix permissions
# USER appuser  # Remove this line

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]