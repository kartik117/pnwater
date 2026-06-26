import logging
from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session, sessionmaker

from pnwater.config import settings
from pnwater.storage.orm import Base

logger = logging.getLogger(__name__)


def make_engine(database_url: str | None = None):
    return create_engine(database_url or settings.database_url, pool_pre_ping=True)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db(bind_engine=None) -> None:
    target = bind_engine or engine
    Base.metadata.create_all(bind=target)
    _try_create_hypertable(target)


def _try_create_hypertable(target) -> None:
    """No-op against SQLite or a Postgres without the TimescaleDB
    extension -- this is genuinely optional, not a required step, so a
    failure here shouldn't take down the whole migration.
    """
    try:
        with target.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            conn.execute(
                text("SELECT create_hypertable('readings', 'recorded_at', if_not_exists => TRUE)")
            )
            conn.commit()
    except (OperationalError, ProgrammingError) as exc:
        logger.info("skipping hypertable creation (not Postgres+TimescaleDB): %s", exc)


def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
