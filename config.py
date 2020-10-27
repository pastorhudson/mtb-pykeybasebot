### config.py ###

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"
import os

DATABASE_URI = os.environ.get("DATABASE_URL")
