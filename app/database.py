from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine(
    url="postgresql://postgres:1423@localhost/fs",
    echo=True
)

SessionLocal = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()