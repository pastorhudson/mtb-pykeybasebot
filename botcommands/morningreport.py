from botcommands.covid import get_covid
from botcommands.meh import get_meh
from botcommands.poll_results import get_polls
from botcommands.stardate import get_stardate
from botcommands.till import get_till
import random


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


def get_morningreport():
    msg = get_obaservation()

    msg += get_stardate()
    msg += get_till(observation=False)
    msg += get_polls()
    msg += get_covid(state="PA", county="Allegheny", observation=False)
    msg += get_covid(state="PA", county="Fayette", observation=False)
    msg += get_meh(observation=False)
    msg += "\n`Daredevil is still blind.`"

    return msg


if __name__ == "__main__":
    print(get_morningreport())
