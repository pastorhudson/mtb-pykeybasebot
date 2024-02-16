import logging
from crud import s
from models import MessageQueue


async def process_message_queue(bot):
    # logging.info("Checking if we have messages")
    # await bot.chat.send('0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d', "Hello World!")

    try:
        # logging.info("Trying to look for messages")
        messages = s.query(MessageQueue).filter(MessageQueue.status == 'PENDING').all()
        # logging.info(f"{len(messages)}")
        for message in messages:
            # logging.info("Iterating messages")
            # logging.info(f"{message.id}: {message.status}")
            # logging.info(f"Message status: {message.status}")
            message.mark_as_processing(s)
            if message.sender != "None":
                msg = f"Incoming Transmission from {message.user.username} via {message.sender}: {message.message}"
            else:
                msg = f"Incoming Transmission from {message.user.username}: {message.message}"

            await bot.chat.send(message.destination, msg)
            message.mark_as_done(s)
        # logging.info("All messages processed")
        return

    except Exception as e:
        logging.info(f"Error: {e}")
    # logging.info("Running message queue")
