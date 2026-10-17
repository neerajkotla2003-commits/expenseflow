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
        username=os.getenv("EXPENSEFLOW_DB_USER", "expenseflow_app"),
        password=os.environ["EXPENSEFLOW_DB_PASSWORD"],
        host=os.getenv("EXPENSEFLOW_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("EXPENSEFLOW_DB_PORT", "3307")),
        database=os.getenv("EXPENSEFLOW_DB_NAME", "expenseflow"),
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