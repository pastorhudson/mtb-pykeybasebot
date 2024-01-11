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
                message.mark_as_processing()
                await bot.chat.send(message.destination, messages.message)
                message.mark_as_processing()
                s.commit()
        return

    except Exception as e:
        logging.info(f"Error: {e}")
    logging.info("Running message queue")
