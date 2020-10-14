from botcommands.sdcompute import Compute
import random
import datetime


def get_stardate():
    observations = ['Finally a task worthy of my vast power.',
                    'I bet you feel smug using this.',
                    "You'll get all the ladies by giving the time in stardate."]

    msg = random.choice(observations)
    now = datetime.datetime.now().timetuple()
    stardate = Compute.sdconvert(now)
    msg += f'```\nStar Date: {stardate}```'

    return msg