import logging
from datetime import datetime


# from crud import s


async def run_db_events(bot):
    ron_marvn = '0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d'
    bot.chat.send(ron_marvn, f'Test Message! {datetime.utcnow()}')
    logging.info("Running db_events")
