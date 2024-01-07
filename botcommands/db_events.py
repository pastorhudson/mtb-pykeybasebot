import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from crud import s
from models import Team, CompletedTasks


async def is_morning_report():
    logging.info("Checking if we have morning report")
    now_utc = datetime.now(timezone.utc)
    # Set to start of the current day (00:00:00)
    start_of_day = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc)

    # Set end of day (start of the next day)
    end_of_day = start_of_day + timedelta(days=1)

    logging.info(f"Today: {now_utc}")
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

                    # SQLAlchemy query
                    morning_report_task = s.query(CompletedTasks) \
                        .filter(CompletedTasks.completed_at >= start_of_day,
                                CompletedTasks.completed_at < end_of_day,
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

        return True

    except Exception as e:
        logging.info(e)
    logging.info("Running db_events")


async def write_morning_report_task(team_name='morethanbits'):
    team = s.query(Team).filter(Team.name.match(team_name)).first()

    completed_task = CompletedTasks(task_name='morning_report', team_id=team.id)
    s.add(completed_task)
    s.commit()
    s.close()
