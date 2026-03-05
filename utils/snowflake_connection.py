import snowflake.connector
import os


def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        account=os.getenv("account"),
        warehouse=os.getenv("warehouse"),
        database=os.getenv("database"),
        schema=os.getenv("schema"),
    )
    return conn
