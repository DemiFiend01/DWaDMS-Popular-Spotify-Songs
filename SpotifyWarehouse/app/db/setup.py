import psycopg
from psycopg.rows import dict_row
from Config import Config

config = Config(user="postgres",
                password="m0rg3n",
                dbname="test_db")

def get_conn():
    return psycopg.connect(user=config.USER,
                           password=config.PASSWORD,
                           dbname=config.DBNAME,
                           row_factory=dict_row)


