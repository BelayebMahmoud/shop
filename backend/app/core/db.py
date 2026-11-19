from collections.abc import Iterator

from sqlalchemy import BigInteger, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    # Ids are BIGINT in db/migrations: bind Python ints as BIGINT too, or a large id overflows int4 (ANO-01).
    type_annotation_map = {int: BigInteger}


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:  # closing without commit rolls back
        yield db
