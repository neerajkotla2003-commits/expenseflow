import os
from functools import lru_cache

from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine():
    database_url = URL.create(
        drivername="mysql+pymysql",
        username="expenseflow_app",
        password=os.environ["EXPENSEFLOW_DB_PASSWORD"],
        host="127.0.0.1",
        port=3307,
        database="expenseflow",
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )


def get_session():
    with Session(get_engine(), expire_on_commit=False) as session:
        yield session


if __name__ == "__main__":
    with get_engine().connect() as connection:
        database_name = connection.execute(
            text("SELECT DATABASE()")
        ).scalar_one()

        print(f"Connected to database: {database_name}")