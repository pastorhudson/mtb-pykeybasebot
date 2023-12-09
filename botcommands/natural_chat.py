import asyncio
import os
from icecream import ic
from pathlib import Path
import base64
from openai import OpenAI, AsyncOpenAI

storage = Path('./storage')

tools = [
    {
        "type": "function",
        "function": {
            "name": "award points",
            "description": "Give points to another user",
            "parameters": {
                "type": "object",
                "properties": {
                    "points": {
                        "type": "int",
                        "description": "The amount of points to award",
                    },
                    "user": {
                        "type": "string",
                        "description": "The user that gets the points.",
                    },
                },
                "required": ["points", "user"],
            },
        }
    },
]

def read_convo():
    try:
        with open(f"{storage.absolute()}/convo.txt", 'r') as file:  # Use file to refer to the file object
            data = file.read()
            data = data.split("\n")
            ic(data)
    except FileNotFoundError:
        data = []
    return data


def get_convo():
    data = read_convo()
    # data.append(f"You: {prompt}\n")
    ic(data)
    write_convo(data)
    return "\n".join(data)


def write_convo(data):
    with open(f"{storage.absolute()}/convo.txt", 'w') as file:  # Use file to refer to the file object
        file.write("\n".join(data))
    return "\n".join(data)


def append_convo(data):
    with open(f"{storage.absolute()}/convo.txt", 'a') as file:  # Use file to refer to the file object
        file.write(data)
    return None


async def get_chat(prompt):
    seed = """"Marvn" is a chatbot with a depressing and sarcastic personality. He is skilled and actually helpful in all things. He is ultimately endeering in a comical dark humor way."""
    client = AsyncOpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    chat_completion = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": seed},
            {"role": "user", "content": get_convo()},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,

        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0
    )

    try:
        return chat_completion.choices[0].message.content
    except:
        return chat_completion.choices[0].message.content.strip()


def get_marvn_reaction(username, msg):
    seed = """"Marvn" is a chatbot with a depressing and sarcastic personality. He is skilled and actually helpful in all things. He is ultimately endeering in a comical dark humor way."""
    client = AsyncOpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": seed},
            {"role": "user", "content": get_convo()},
            {"role": "user", "content": f"@{username}: {msg}"}
            ]
    )

    try:
        return chat_completion.choices[0].message.content
    except:
        return chat_completion.choices[0].message.content.strip()


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


async def get_chat_with_image(image_path, prompt):
    base64_image = await asyncio.to_thread(encode_image, image_path)

    seed = """"Marvn" is a chatbot with a depressing and sarcastic personality. He is skilled and actually helpful in all things. He is ultimately endearing in a comical dark humor way."""
    client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    chat_complettion = await client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": seed},
            {"role": "user", "content": await asyncio.to_thread(get_convo)},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.7,
        max_tokens=4096,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0
    )
    try:
        return chat_complettion.choices[0].message.content
    except:
        return chat_complettion.choices[0].message.content.strip()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(get_gpt_summary('https://youtu.be/itAMIIBnZ-8?si=P795Yp3TMeewBdeq'))
    img = 'C://Users//geekt//Downloads//ds9meme.png'
    prompt = "What's going on with this image??"

    result = loop.run_until_complete(get_chat_with_image(img, prompt))
    print(result)


    # ic(os.getenv("OPENAI_API_KEY"))
    # print(get_convo())
    # img = 'C://Users//geekt//Downloads//ds9meme.png'
    # prompt = "What's going on with this image??"
    # print(get_chat_with_image(img, prompt))
    # print(get_chat(prompt))
