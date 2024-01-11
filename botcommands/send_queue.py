import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from crud import s
from models import MessageQueue


async def process_message_queue(bot):
    logging.info("Checking if we have messages")

    # Get current date in 'America/New_York' timezone
    now_time_ny = datetime.now(ZoneInfo('America/New_York'))

    logging.info(f"Local Time (America/New_York): {now_time_ny}")

    try:
        messages = s.query(MessageQueue).all()
        for message in messages:
            if message.status == 'PENDING':
                logging.info(f"Message status: {message.status}")
                await bot.chat.send('0000f057aa01b5cb1b8b675b323baf88d349dc1d14e6a5cd605c2ac5cfacff30', messages.message)
        return

    except Exception as e:
        logging.info(f"Error: {e}")
    logging.info("Running message queue")


async def write_morning_report_task(team_name='morethanbits'):
    team = s.query(Team).filter(Team.name.match(team_name)).first()

    completed_task = CompletedTasks(task_name='morning_report', team_id=team.id)
    s.add(completed_task)
    s.commit()
    s.close()
