import asyncio
from pathlib import Path
from pprint import pprint

import aiohttp
from openai import AsyncOpenAI
import os


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


async def generate_dalle_image(prompt):
    client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url
    revised_prompt = f"Revised Prompt:```{response.data[0].revised_prompt}```"

    return {
        "msg": "\n".join([prompt, revised_prompt]),
        "file": await download_image(image_url, 'Dall-e-3_img.png')
    }


async def restyle_image(image_path, style_prompt):
    """
    Restyles an existing image according to a style prompt using OpenAI's API.

    Args:
        image_path (str): Path to the image file to be restyled
        style_prompt (str): Description of the style to apply to the image

    Returns:
        dict: Contains the original prompt and file path of the restyled image
    """
    import os
    from openai import AsyncOpenAI
    from botcommands.utils import download_image

    client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # Open the image file properly - don't convert to base64
    with open(image_path, "rb") as image_file:
        # Pass the file object directly to the API
        response = await client.images.edit(
            image=image_file,  # Pass the file handle directly
            prompt=style_prompt,
            model="dall-e-2",
            size="1024x1024",
            n=1,
        )

    image_url = response.data[0].url

    # Check if revised_prompt exists in response
    revised_prompt = ""
    if hasattr(response.data[0], 'revised_prompt'):
        revised_prompt = f"\nRevised Prompt: ```{response.data[0].revised_prompt}```"

    return {
        "msg": f"Style prompt: {style_prompt}{revised_prompt}",
        "file": await download_image(image_url, 'Restyled_image.png')
    }

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(generate_dalle_image('A cool spaceship'))

    pprint(result)
