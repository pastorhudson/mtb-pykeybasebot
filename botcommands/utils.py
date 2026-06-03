import logging
import subprocess
from pathlib import Path

import aiohttp

from models import Team, User
import base64
import os
from datetime import datetime


def get_team_user(team_name, username):
    from crud import s

    team = s.query(Team).filter_by(name=team_name).first()
    user = s.query(User).filter_by(username=username).first()

    return team, user


def get_team(team_name):
    from crud import s

    team = s.query(Team).filter_by(name=team_name).first()

    return team


async def set_unfurl(bot, unfurl):
    if unfurl:
        furl = await bot.chat.execute(
            {"method": "setunfurlsettings",
             "params": {"options": {"mode": "always"}}})
    else:
        furl = await bot.chat.execute(
            {"method": "setunfurlsettings",
             "params": {"options": {"mode": "never"}}})
    return


async def download_image(pic_url, file_name='meh.png'):
    storage = Path('./storage')

    async with aiohttp.ClientSession() as session:
        async with session.get(pic_url) as response:
            if response.status != 200:
                return None

            file_path = f"{storage.absolute()}/{file_name}"

            with open(file_path, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

            return file_path


def save_base64_image(image_base64, output_dir="storage", file_prefix="image"):
    """
    Saves base64 decoded image data to a file

    Args:
        image_base64: The decoded base64 image data (already processed with base64.b64decode)
        output_dir: Directory to save the image (default: 'images')
        file_prefix: Prefix for the filename (default: 'image')

    Returns:
        Tuple containing (file path, filename)
    """
    storage = Path('./storage')
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{file_prefix}_{timestamp}.png"
    # filepath = os.path.join(output_dir, filename)
    file_path = f"{storage.absolute()}/{filename}"

    # Write the binary image data to file
    with open(file_path, 'wb') as f:
        f.write(image_base64)

    return file_path

import struct

def _sample_amplitudes(mp3_path: str, num_buckets: int = 53) -> list:
    """Sample RMS amplitudes from audio for waveform display."""
    pcm_path = mp3_path + '.pcm'
    try:
        subprocess.run([
            '/usr/bin/ffmpeg', '-y', '-i', mp3_path,
            '-ac', '1',        # mono
            '-ar', '8000',     # 8kHz is plenty for amplitude sampling
            '-f', 's16le',     # raw 16-bit signed PCM
            pcm_path
        ], check=True, capture_output=True)

        with open(pcm_path, 'rb') as f:
            raw = f.read()

        num_samples = len(raw) // 2
        samples = struct.unpack(f'<{num_samples}h', raw)

        bucket_size = max(1, num_samples // num_buckets)
        amps = []
        for i in range(num_buckets):
            bucket = samples[i * bucket_size:(i + 1) * bucket_size]
            if bucket:
                rms = (sum(s * s for s in bucket) / len(bucket)) ** 0.5
                # Normalize to ~0.0-0.4 range matching real voice memos
                amps.append(round(min(rms / 32768.0 * 2.5, 0.4), 6))
            else:
                amps.append(0.0)
        return amps

    except Exception as e:
        logging.error(f"Amplitude sampling failed: {e}")
        return []
    finally:
        if os.path.exists(pcm_path):
            os.unlink(pcm_path)


def _to_voice_mp4(mp3_path: str) -> dict:
    """Rewrap mp3 as AAC-in-mp4 with mobile-compatible metadata."""
    mp4_path = mp3_path.replace('.mp3', '.mp4')

    subprocess.run([
        '/usr/bin/ffmpeg', '-y', '-i', mp3_path,
        '-vn',  # no video stream at all
        '-acodec', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',  # moov atom at front
        '-map_metadata', '-1',  # strip all metadata
        '-fflags', '+bitexact',  # deterministic output
        mp4_path
    ], check=True, capture_output=True)

    amps = _sample_amplitudes(mp3_path)
    return {'file': mp4_path, 'audio_amps': amps}