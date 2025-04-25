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