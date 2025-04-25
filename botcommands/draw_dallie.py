import asyncio
import logging
from pathlib import Path
from pprint import pprint
import aiohttp
import openai
from openai import OpenAI
import base64
import logging
import os
from openai import AsyncOpenAI
from botcommands.utils import save_base64_image


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
        "msg": revised_prompt,
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
    client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    logging.info(f"Creating variation of image: {image_path}")
    logging.info(f"Style description (for reference only): {style_prompt}")

    try:
        # Open the image file in binary mode
        with open(image_path, "rb") as image_file:
            result = await client.images.edit(
                model="gpt-image-1",
                image=image_file,
                prompt=style_prompt,
            )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        result_path = save_base64_image(image_bytes)

        logging.info(f"Successfully created image variation. Saved to: {result_path}")

        return {
            "msg": f"Created a variation of your image using style: \"{style_prompt}\"",
            "file": result_path
        }

    except Exception as e:
        logging.error(f"Error creating image variation: {str(e)}")
        return {
            "msg": f"Sorry, I couldn't create a variation of your image. Error: {str(e)}"
        }


async def draw_gpt_image(prompt):
    try:
        client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        result = await client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            moderation='low'
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        result_path = save_base64_image(image_bytes)

        logging.info(f"Successfully created image variation. Saved to: {result_path}")

        return {
            "msg": prompt,
            "file": result_path
        }

    except openai.BadRequestError as e:
        error_message = str(e)
        logging.error(f"BadRequestError: {error_message}")
        return {
            "msg": f"Image generation failed: {error_message}",
            "file": None
        }
    except Exception as e:
        error_message = str(e)
        logging.error(f"Unexpected error: {error_message}")
        return {
            "msg": f"An unexpected error occurred: {error_message}",
            "file": None
        }



if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(draw_gpt_image('Vladamir Putin Riding a Unicorn'))
    # result = loop.run_until_complete(restyle_image('.\storage\image_20250425_005154.png', 'Make this ultra realistic'))
    pprint(result)
