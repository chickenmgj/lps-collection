import os
from pathlib import Path

import pymysql.cursors
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class MySQLConnection:

    def __init__(self, db=None):
        database_name = os.getenv("MYSQL_DATABASE") or db

        self.connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=database_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            ssl={
                "ca": os.getenv("MYSQL_SSL_CA")
                } if os.getenv("MYSQL_SSL_CA") else None
        )

    def query_db(self, query, data=None):
        if data is None:
            data = {}

        try:
            with self.connection.cursor() as cursor:
                print("Running Query:", cursor.mogrify(query, data))
                cursor.execute(query, data)

                query_type = query.strip().lower()

                if query_type.startswith("insert"):
                    return cursor.lastrowid

                if query_type.startswith("select"):
                    return cursor.fetchall()

                return True

        except Exception as error:
            print("Something went wrong:", error)
            return False

        finally:
            self.connection.close()


def connectToMySQL(db=None):
    return MySQLConnection(db)