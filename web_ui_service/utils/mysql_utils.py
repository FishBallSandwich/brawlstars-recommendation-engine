from sqlalchemy import create_engine, URL
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

username = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")


def connect_to_mysql():
    try:
        url_object = URL.create(
            drivername="mysql+mysqlconnector",
            username=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            database=os.getenv("MYSQL_DB"),
            query={"charset": "utf8mb4"},
        )

        engine = create_engine(url_object)
        print("Successfully created SQLAlchemy engine.")
        return engine

    except Exception as e:
        print(f"Error creating SQLAlchemy engine: {e}")
        return None


def load_into_mysql(df, engine, table_name):
    try:
        with engine.begin() as connection:
            print(f"Loading into table {table_name}")
            df.to_sql(name=table_name, con=connection, if_exists="append", index=False)
            print("success loading table")
    except Exception as err:
        print(err)
        return None


def mysql_to_df(engine, sql):
    try:
        with engine.begin() as connection:
            print("retrieving table")
            df = pd.read_sql(sql, con=connection)
            print("retrieved table to df")
            return df
    except Exception as err:
        print(err)
        return None
