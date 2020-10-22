from botcommands.sdcompute import Compute
import random
import datetime


def get_observation():
    observations = ['Finally a task worthy of my vast power.',
                    'I bet you feel smug using this.',
                    "You'll get all the ladies by giving the time in stardate."]
    return random.choice(observations)


def get_stardate(sd=None, observation=True):
    msg = ""

    if observation:
        msg = get_observation()
    if sd:
        try:
            sd = float(sd)
            earthdate = Compute.sdtranslate(sd)
            msg += f'```\nEarth Date: {earthdate}```'
        except ValueError:
            msg = "You have failed to provide a proper stardate. I'm not suprised."
    else:
        now = datetime.datetime.now().timetuple()
        stardate = Compute.sdconvert(now)
        msg += f'```\nStar Date: {stardate}```'

    return msg


if __name__ == '__main__':
    print(get_stardate(observation=False))