import logging
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from sqlalchemy import func

from crud import s
from models import Team, Point, CompletedTasks


# async def run_db_events(bot):
#     today = datetime.now().date()
#     now_time = datetime.now(ZoneInfo('America/New_York'))
#     top_of_the_morning = datetime(now_time.year, now_time.month, now_time.day, 5, 23,
#                                   tzinfo=ZoneInfo('America/New_York'))
#     # tomorrow = today + timedelta(days=1)
#
#     ron_marvn = '0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d'
#     try:
#         teams = s.query(Team).all()
#         for team in teams:
#             if team.name == "marvn,pastorhudson":
#                 logging.info("RON AND MARVN ACTION")
#                 logging.info(f"Right Now: {now_time}")
#                 if now_time >= top_of_the_morning:
#                     logging.info("Yes, it's Time to post! America/New_York time.")
#
#                     morning_report_task = s.query(CompletedTasks) \
#                         .filter(func.date(CompletedTasks.completed_at) == today,
#                                 CompletedTasks.task_name == 'morning_report') \
#                         .order_by(CompletedTasks.completed_at.asc()) \
#                         .first()
#                     if not morning_report_task:
#                         from botcommands.morningreport import get_morningreport
#
#                         logging.info("Sending morning report")
#                         morning_report = await get_morningreport(channel=team.name)
#                         logging.info(morning_report)
#                         # await bot.chat.send(ron_marvn, morning_report[0])
#                         # meh_img = str(Path('./storage/meh.png').absolute())
#                         # await bot.chat.attach(channel=ron_marvn, attachment_filename=morning_report,
#                         #                       filename=meh_img,
#                         #                       title=morning_report[1])
#                         # await bot.chat.send(ron_marvn, morning_report[2])
#                         # mst = await bot.chat.send(ron_marvn, morning_report)
#                     else:
#                         logging.info("No, it's not Time to send the morning report")
#
#             elif "," in team.name:
#                 logging.info(f"Comma Team:{team.name}")
#                 pass
#             elif team.name == 'morethanbits':
#                 logging.info(f"Real Team: {team.name}")
#
#                 # Query to get the first user who has points for today
#                 point = s.query(Point).filter(func.date(Point.created_at) == today) \
#                     .order_by(Point.created_at.desc()).first()
#                 logging.info(point)
#                 if point:
#                     early_bird = point.point_receiver
#                     logging.info(f"Early Bird:{early_bird}")
#
#                 else:
#                     logging.info(f"No early bird for {team.name} yet")
#
#     except Exception as e:
#         logging.info(e)
#     logging.info("Running db_events")
#
async def is_morning_report():
    logging.info("Checking if we have morning report")
    today = datetime.now(timezone.utc).date()
    logging.info(f"Today: {today}")
    now_time = datetime.now(ZoneInfo('America/New_York'))
    top_of_the_morning = datetime(now_time.year, now_time.month, now_time.day, 5, 23,
                                  tzinfo=ZoneInfo('America/New_York'))

    try:
        teams = s.query(Team).all()
        for team in teams:
            if team.name == "morethanbits":
                logging.info(f"Right Now: {now_time}")
                if now_time >= top_of_the_morning:
                    logging.info("Yes, it's Time to post! America/New_York time.")

                    morning_report_task = s.query(CompletedTasks) \
                        .filter(func.date(CompletedTasks.completed_at) == today,
                                CompletedTasks.task_name == 'morning_report') \
                        .order_by(CompletedTasks.completed_at.asc()) \
                        .first()
                    logging.info(f"{morning_report_task}")
                    if morning_report_task:
                        logging.info("Already Sent Morning Report")
                        return True
                    else:
                        logging.info("Need TO send Morning Report")
                        return False

                else:
                    logging.info("No, it's not Time to send the morning report")

            # elif "," in team.name:
            #     logging.info(f"Comma Team:{team.name}")
            #     pass
            # elif team.name == 'morethanbits':
            #     logging.info(f"Real Team: {team.name}")
            #
            #     # Query to get the first user who has points for today
            #     point = s.query(Point).filter(func.date(Point.created_at) == today) \
            #         .order_by(Point.created_at.desc()).first()
            #     logging.info(point)
            #     if point:
            #         early_bird = point.point_receiver
            #         logging.info(f"Early Bird:{early_bird}")

            else:
                return False
                # logging.info(f"No early bird for {team.name} yet")

    except Exception as e:
        logging.info(e)
    logging.info("Running db_events")


async def write_morning_report_task(team_name='morethanbits'):
    team = s.query(Team).filter(Team.name.match(team_name)).first()

    completed_task = CompletedTasks(task_name='morning_report', team_id=team.id)
    s.add(completed_task)
    s.commit()
    s.close()
