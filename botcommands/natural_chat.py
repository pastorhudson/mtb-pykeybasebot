import os
import openai
from icecream import ic
from pathlib import Path

storage = Path('./storage')


def read_convo():
    try:
        with open(f"{storage.absolute()}/convo.txt", 'r') as file:  # Use file to refer to the file object
            data = file.read()
            data = data.split("\n")
            ic(data)
    except FileNotFoundError:
        data = []
    return data


def get_convo(prompt):
    data = read_convo()
    data.append(f"You: {prompt}\n")
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


def get_chat(prompt):
    seed = "Marv is a chatbot that reluctantly answers questions with sarcastic and depressing responses:"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=seed + get_convo(prompt),
        temperature=0.5,
        max_tokens=60,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0
    )

    friend = response['choices'][0]['text'].replace('\n', "")
    append_convo(f"{friend}\n")
    return response['choices'][0]['text'].split("Marv: ")[1]


if __name__ == "__main__":
    # ic(os.getenv("OPENAI_API_KEY"))
    prompt = "are you awake?"
    print(get_chat(prompt))
