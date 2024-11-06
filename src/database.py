import sqlalchemy
from src import database as db
import os
import dotenv
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)
metadata_obj = sqlalchemy.MetaData()
customers = sqlalchemy.Table("cart", metadata_obj, autoload_with=engine)
potions = sqlalchemy.Table("potions_ledger", metadata_obj, autoload_with=engine)
gold = sqlalchemy.Table("gold_ledger", metadata_obj, autoload_with=engine)

