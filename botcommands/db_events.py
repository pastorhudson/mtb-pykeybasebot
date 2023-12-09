import logging
from datetime import datetime
from crud import s
from models import Team


async def run_db_events(bot):
    ron_marvn = '0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d'
    teams = s.query(Team).all()
    for team in teams:
        if team.name == ron_marvn:
            logging.info("RON AND MARVN ACTION")
        elif "," in team.name:
            logging.info(f"Comma Team:{team.name}")
        else:
            logging.info(f"Real Team: {team.name}")
    early_bird = None
    mst = await bot.chat.send(ron_marvn, f'Test Message! {datetime.utcnow()}')
    logging.info("Running db_events")
