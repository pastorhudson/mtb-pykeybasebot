import io
import os
import openai
from icecream import ic


def read_convo():
    try:
        with open("convo.txt", 'r') as file:  # Use file to refer to the file object
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
    with open("convo.txt", 'w') as file:  # Use file to refer to the file object
        file.write("\n".join(data))
    return "\n".join(data)


def append_convo(data):
    with open("convo.txt", 'a') as file:  # Use file to refer to the file object
        file.write(data)
    return None


def get_chat(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=get_convo(prompt),
        temperature=0.5,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0,
        stop=["You:"]
    )
    friend = response['choices'][0]['text'].replace('\n', "")
    append_convo(f"Friend: {friend}\n")
    return response['choices'][0]['text']


if __name__ == "__main__":
    # ic(os.getenv("OPENAI_API_KEY"))
    prompt = "I guess it's red on the inside."
    ic(get_chat(prompt))
