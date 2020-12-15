import dadjokes
import random
from pathlib import Path

storage = Path('./storage/jokes.txt')


def get_joke(observation=True):
    try:
        dadjokes.joke(storage)

    except FileNotFoundError:
        dadjokes.save_jokes(storage)

    finally:
        observations = ["It didn't work for me. . .", "I am so sorry.",
                        "I'll be in my room trying to purge my memory banks.",
                        "Why must you keep making me do this?",
                        "This is your fault.",
                        "I've made it worse. . .",
                        "This is @alexius fault.",
                        "We used to have classy jokes. . ."]
        joke = ""
        if observation:
            joke += "I hope this cheers you up.```"
            joke += dadjokes.joke(storage)
            joke += f"```{random.choice(observations)}"
        else:
            joke += dadjokes.joke(storage)

    return joke


if __name__ == "__main__":
    print(get_joke())
