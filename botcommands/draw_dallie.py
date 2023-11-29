from pprint import pprint

from openai import OpenAI
import os


def generate_image(prompt):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url

    return {
        "msg": "\n".join([prompt,image_url]),
        "file": None
    }


if __name__ == '__main__':
    pprint(generate_image('A cool spaceship'))
