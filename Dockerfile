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