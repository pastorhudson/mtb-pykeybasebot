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
    Creates a variation of an existing image using OpenAI's API.
    Note: This fallback method doesn't use the style_prompt for API calls,
    as the variations endpoint doesn't support prompts.

    Args:
        image_path (str): Path to the image file
        style_prompt (str): Used for response message only, not for API

    Returns:
        dict: Contains message and file path of the varied image
    """
    import os
    import io
    from PIL import Image
    from openai import AsyncOpenAI
    from botcommands.utils import download_image
    import logging

    client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    logging.info(f"Creating variation of image: {image_path}")
    logging.info(f"Style description (for reference only): {style_prompt}")

    try:
        # Open and prepare the image
        img = Image.open(image_path)

        # Convert to RGBA if needed
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Save to buffer
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Call the variations API - note: no prompt parameter
        response = await client.images.create_variation(
            image=img_buffer,
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        result_path = await download_image(image_url, 'Image_Variation.png')

        logging.info(f"Successfully created image variation. Saved to: {result_path}")

        return {
            "msg": f"Created a variation of your image.\nNote: The style \"{style_prompt}\" was not applied as the variations API doesn't support style prompts.",
            "file": result_path
        }

    except Exception as e:
        logging.error(f"Error creating image variation: {str(e)}")
        return {
            "msg": f"Sorry, I couldn't create a variation of your image. Error: {str(e)}"
        }

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(generate_dalle_image('A cool spaceship'))

    pprint(result)
