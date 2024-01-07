from botcommands.meh import get_meh
from botcommands.stardate import get_stardate
from botcommands.till import get_till
from botcommands.school_closings import get_school_closings
import random
from botcommands.scorekeeper import get_score
from botcommands.jokes import get_joke
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import func
from crud import s
from models import Team, Point, CompletedTasks

logging.basicConfig(level=logging.DEBUG)


def get_obaservation():
    observations = ["Unfortunately I'm still here.",
                    "You had to wake me up and remind me I'm sentient.",
                    "Oh what a dreary morning.",
                    "I wish I were blind.",
                    "You know I'm not keeping score right?"]
    return random.choice(observations)


async def get_morningreport(channel):
    schools = ["Albert Gallatin", "Uniontown", "North Hills"]
    closings = get_school_closings(schools)
    team = s.query(Team).filter_by(name=channel).first()

    msg = ["", "", "", "", ""]

    msg[0] = get_obaservation() + "\n"
    msg[0] += "`" + get_stardate(observation=False).strip("`") + "`\n"

    meh = await get_meh(observation=True)
    msg[1] = "\nMeh:" + meh
    msg[2] = f"\n\n{get_score(channel)}"
    msg[2] += get_till(team_name=team.name, observation=False)
    msg[2] += f"Today's Joke:```{get_joke(False)}```"
    closings, no_school = get_school_closings(schools, observations=False)
    if no_school:
        msg[3] += closings['msg']
    s.close()
    return msg


async def run_db_events(bot):
    today = datetime.now().date()
    now_time = datetime.now(ZoneInfo('America/New_York'))
    top_of_the_morning = datetime(now_time.year, now_time.month, now_time.day, 5, 23,
                                  tzinfo=ZoneInfo('America/New_York'))
    # tomorrow = today + timedelta(days=1)

    ron_marvn = '0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d'
    try:
        teams = s.query(Team).all()
        for team in teams:
            if team.name == "marvn,pastorhudson":
                logging.info("RON AND MARVN ACTION")
                logging.info(f"Right Now: {now_time}")
                if now_time >= top_of_the_morning:
                    logging.info("Yes, it's Time to post! America/New_York time.")

                    morning_report_task = s.query(CompletedTasks) \
                        .filter(func.date(CompletedTasks.completed_at) == today,
                                CompletedTasks.task_name == 'morning_report') \
                        .order_by(CompletedTasks.completed_at.asc()) \
                        .first()
                    if not morning_report_task:

                        logging.info("Sending morning report")
                        morning_report = await get_morningreport(channel=team.name)
                        logging.info(morning_report)
                        # await bot.chat.send(ron_marvn, morning_report[0])
                        # meh_img = str(Path('./storage/meh.png').absolute())
                        # await bot.chat.attach(channel=ron_marvn, attachment_filename=morning_report,
                        #                       filename=meh_img,
                        #                       title=morning_report[1])
                        # await bot.chat.send(ron_marvn, morning_report[2])
                        # mst = await bot.chat.send(ron_marvn, morning_report)
                    else:
                        logging.info("No, it's not Time to send the morning report")

            elif "," in team.name:
                logging.info(f"Comma Team:{team.name}")
                pass
            elif team.name == 'morethanbits':
                logging.info(f"Real Team: {team.name}")

                # Query to get the first user who has points for today
                point = s.query(Point).filter(func.date(Point.created_at) == today) \
                    .order_by(Point.created_at.desc()).first()
                logging.info(point)
                if point:
                    early_bird = point.point_receiver
                    logging.info(f"Early Bird:{early_bird}")

                else:
                    logging.info(f"No early bird for {team.name} yet")

    except Exception as e:
        logging.info(e)
    logging.info("Running db_events")


if __name__ == "__main__":
    # channel_members = {'owners': [{'uid': 'f4089cdf5fc8ebe433d5b9f49b66d619', 'username': 'pastorhudson', 'fullName': 'Ron Hudson'}, {'uid': 'a5465087aede61be961a6bb3bf964f19', 'username': 'morethanmarvin', 'fullName': ''}], 'admins': [], 'writers': [], 'readers': [], 'bots': [], 'restrictedBots': []}
    get_morningreport('morethanmarvin,pastorhudson')
    # print(get_score(channel_members))
