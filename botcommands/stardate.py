from botcommands.sdcompute import Compute
import random
import datetime


def get_stardate(sd=None):
    print(sd)
    observations = ['Finally a task worthy of my vast power.',
                    'I bet you feel smug using this.',
                    "You'll get all the ladies by giving the time in stardate."]

    msg = random.choice(observations)
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