import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from crud import s
from models import Team, CompletedTasks


async def is_morning_report():
    logging.info("Checking if we have a morning report")

    # Get current date in 'America/New_York' timezone
    now_time_ny = datetime.now(ZoneInfo('America/New_York'))
    logging.info(f"Local Time (America/New_York): {now_time_ny}")

    # Define start and end of the current day in 'America/New_York'
    start_of_day_ny = datetime(now_time_ny.year, now_time_ny.month, now_time_ny.day, tzinfo=ZoneInfo('America/New_York'))
    end_of_day_ny = start_of_day_ny + timedelta(days=1)

    # Convert start and end times to UTC
    start_of_day_utc = start_of_day_ny.astimezone(timezone.utc)
    end_of_day_utc = end_of_day_ny.astimezone(timezone.utc)

    try:
        teams = s.query(Team).all()
        for team in teams:
            if team.name == "morethanbits":
                logging.info(f"Checking tasks for today in America/New_York timezone")

                # SQLAlchemy query to find morning report tasks completed today in NY time
                morning_report_task = s.query(CompletedTasks) \
                        .filter(CompletedTasks.completed_at >= start_of_day_utc,
                                CompletedTasks.completed_at < end_of_day_utc,
                                CompletedTasks.task_name == 'morning_report') \
                        .order_by(CompletedTasks.completed_at.asc()) \
                        .first()

                if morning_report_task:
                    logging.info(f"Morning Report already sent today at {morning_report_task.completed_at_in_ny()}")
                    return True
                else:
                    logging.info("No Morning Report sent today yet")
                    return False
        return False

    except Exception as e:
        logging.info(f"Error: {e}")
    logging.info("Running db_events")


async def write_morning_report_task(team_name='morethanbits'):
    team = s.query(Team).filter(Team.name.match(team_name)).first()

    completed_task = CompletedTasks(task_name='morning_report', team_id=team.id)
    s.add(completed_task)
    s.commit()
    s.close()
