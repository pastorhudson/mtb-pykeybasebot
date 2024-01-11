import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from crud import s
from models import MessageQueue


async def process_message_queue(bot):
    logging.info("Checking if we have messages")

    try:
        logging.info("Trying to look for messages")
        messages = s.query(MessageQueue).all()
        logging.info(f"{len(messages)}")
        for message in messages:
            logging.info("Iterating messages")
            if message.status == 'PENDING':
                logging.info(f"Message status: {message.status}")
                message.mark_as_processing()
                await bot.chat.send(message.destination, messages.message)
                message.mark_as_processing()
                s.commit()
        logging.info("All messages processed")
        return

    except Exception as e:
        logging.info(f"Error: {e}")
    logging.info("Running message queue")
