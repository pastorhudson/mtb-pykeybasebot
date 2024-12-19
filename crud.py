### crud.py ###
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

# Get database URL and handle Heroku's postgres:// vs postgresql:// issue
database_url = os.environ.get("DATABASE_URL")
if database_url is None:
    raise ValueError("DATABASE_URL environment variable is not set")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Create engine with error handling
try:
    engine = create_engine(database_url, pool_pre_ping=True)
except Exception as e:
    print(f"Failed to create database engine: {str(e)}")
    raise

Session = sessionmaker(bind=engine)


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


s = Session()