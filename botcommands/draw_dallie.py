from pprint import pprint

from openai import OpenAI
import os


def generate_dalle_image(prompt):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url
    revised_prompt = f"Revised Prompt:```{response.data[0].revised_prompt}```"

    return {
        "msg": "\n".join([prompt, image_url, revised_prompt]),
        "file": None
    }


if __name__ == '__main__':
    pprint(generate_dalle_image('A cool spaceship'))
