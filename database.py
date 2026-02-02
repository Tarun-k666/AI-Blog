from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./blog.db'

engine= create_engine(
    url=SQL_ALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

sessionLocal = sessionmaker(autoflush= False, autocommit= False, bind=engine)

class Base(DeclarativeBase):
    pass


def get_db():
    with sessionLocal() as db:
        yield db