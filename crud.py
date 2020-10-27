### crud.py ###
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine(os.environ.get("DATABASE_URL"))
Session = sessionmaker(bind=engine)


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


s = Session()
