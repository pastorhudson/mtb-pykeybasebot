import logging
import subprocess
from pathlib import Path
import struct
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


def _sample_amplitudes(audio_path: str, num_buckets: int = 53) -> list:
    """Sample RMS amplitudes from any audio file for waveform display."""
    pcm_path = audio_path + '.pcm'
    try:
        subprocess.run([
            '/usr/bin/ffmpeg', '-y', '-i', audio_path,
            '-ac', '1', '-ar', '8000', '-f', 's16le', pcm_path
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


from PIL import Image, ImageDraw


def _generate_waveform_png(amps: list, output_path: str,
                           width: int = 106, height: int = 64):
    """Generate a waveform preview PNG matching Keybase voice memo dimensions."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bar_count = len(amps)
    bar_width = max(1, width // (bar_count * 2))
    spacing = width / bar_count

    for i, amp in enumerate(amps):
        bar_height = max(2, int(amp * height * 2.5))
        x = int(i * spacing + spacing / 2)
        y_center = height // 2
        # Green color like Keybase voice memos
        draw.rectangle(
            [x - bar_width, y_center - bar_height // 2,
             x + bar_width, y_center + bar_height // 2],
            fill=(77, 210, 100, 255)
        )

    img.save(output_path, 'PNG')
    return output_path


def to_voice_mp4(audio_path: str) -> dict:
    """
    Convert any audio file to Keybase voice memo format.
    Returns dict with 'file' (mp4 path), 'preview' (png path), 'audio_amps', 'duration_ms'.
    """
    mp4_path = os.path.splitext(audio_path)[0] + '_voice.mp4'
    png_path = os.path.splitext(audio_path)[0] + '_preview.png'

    subprocess.run([
        '/usr/bin/ffmpeg', '-y', '-i', audio_path,
        '-vn', '-acodec', 'aac', '-b:a', '128k',
        '-ac', '1', '-ar', '44100',
        '-map_metadata', '-1',
        '-movflags', '+faststart',
        mp4_path
    ], check=True, capture_output=True)

    # Get duration
    probe = subprocess.run([
        '/usr/bin/ffprobe', '-v', 'quiet',
        '-print_format', 'json', '-show_streams', audio_path
    ], capture_output=True, text=True)
    duration_ms = 0
    try:
        import json
        streams = json.loads(probe.stdout).get('streams', [])
        if streams:
            duration_ms = int(float(streams[0].get('duration', 0)) * 1000)
    except Exception:
        pass

    amps = _sample_amplitudes(audio_path)
    _generate_waveform_png(amps, png_path)

    return {
        'file': mp4_path,
        'preview': png_path,
        'audio_amps': amps,
        'duration_ms': duration_ms,
    }