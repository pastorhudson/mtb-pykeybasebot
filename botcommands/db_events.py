import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import func
from crud import s
from models import Team, Point, User


async def run_db_events(bot):
    today = datetime.now().date()
    now = datetime.now(ZoneInfo('America/New_York'))
    tomorrow = today + timedelta(days=1)

    ron_marvn = '0000c3e1daf296e6c893a02f6ae2e39bbe99ecfbdc7bec6daccb3fd9efb0382d'
    try:
        teams = s.query(Team).all()
        for team in teams:
            if team.name == ron_marvn:
                # logging.info("RON AND MARVN ACTION")
                pass
            elif "," in team.name:
                # logging.info(f"Comma Team:{team.name}")
                pass
            else:
                logging.info(f"Real Team: {team.name}")

                # Query to get the first user who has points for today
                point = s.query(Point).filter(func.date(Point.created_at) == today) \
                    .order_by(Point.created_at.asc()).first()
                logging.info(point)
                if point:
                    logging.info(f"user:{point.point_receiver}")
                    early_bird = point.point_receiver

                else:
                    logging.info(f"No early bird for {team.name} yet")
            # if now.hour == 5 and now.minute == 23:
            #     logging.info("Yes, it's 5:23am America/New_York time.")
            # else:
            #     logging.info("No, it's not 5:23am America/New_York time.")
            if now.hour == 13 and now.minute == 35:
                logging.info("Yes, it's 1:35pm America/New_York time.")
            else:
                logging.info("No, it's not 1:35pm America/New_York time.")
    #     mst = await bot.chat.send(ron_marvn, f'Test Message! {datetime.utcnow()}')
    except Exception as e:
        logging.info(e)
    logging.info("Running db_events")
