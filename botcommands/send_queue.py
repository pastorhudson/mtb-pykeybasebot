import logging
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from crud import s
from models import MessageQueue


async def process_message_queue(bot):
    logging.info("Checking if we have messages")
    await bot.chat.send('0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d', "Hello World!")

    try:
        logging.info("Trying to look for messages")
        messages = s.query(MessageQueue).all()
        logging.info(f"{len(messages)}")
        for message in messages:
            logging.info("Iterating messages")
            logging.info(f"{message.message_id}: {message.status}")
            if message.status == 'PENDING':
                logging.info(f"Message status: {message.status}")
                message.mark_as_processing()
                await bot.chat.send(message.destination, message.message)
                message.mark_as_processing()
                s.commit()
        logging.info("All messages processed")
        return

    except Exception as e:
        logging.info(f"Error: {e}")
    logging.info("Running message queue")
