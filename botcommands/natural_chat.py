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


def get_chat(prompt):
    seed = """"Marvn" is a chatbot with a depressing and sarcastic personality. He is skilled and actually helpful in all things. He is ultimately endeering in a comical dark humor way."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": seed},
            {"role": "user", "content": get_convo()},
            {"role": "user", "content": prompt }
        ],
        temperature=0.7,

        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0
    )

    friend = response.choices[0].message
    append_convo('Request:' + prompt + '\n\n')
    append_convo(f"marvn: {friend['content']}\n\n")
    try:
        return response.choices[0].message['content']
    except:
        return response.choices[0].message['content'].strip()

def get_marvn_reaction(username, msg):
    seed = f""""Marvn" is a chatbot that reluctantly answers questions with sarcastic and depressing responses:  @{username}: {msg} """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=seed,
        temperature=0.5,
        max_tokens=500,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0
    )

    friend = response['choices'][0]['text'].replace('\n', "")
    append_convo(f"{friend}\n")
    try:
        return response['choices'][0]['text'].split("Marvn:")[1].strip()
    except:
        return response['choices'][0]['text'].strip()


if __name__ == "__main__":
    # ic(os.getenv("OPENAI_API_KEY"))
    prompt = "Correct this to standard English:\n\n" \
             "Dogs like chicken aaa."
    print(get_chat(prompt))
