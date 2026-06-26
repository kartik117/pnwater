import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReadingRow(Base):
    """A TimescaleDB hypertable in Postgres, a plain table in SQLite
    (tests). `create_hypertable` is issued separately in db.py with
    `if_not_exists` and is a no-op (silently skipped) against a backend
    that doesn't have the extension -- see init_db().

    Primary key is (id, recorded_at), not just id: TimescaleDB requires
    the partitioning column to be part of every unique constraint on a
    hypertable, since uniqueness can't be cheaply enforced across
    partitions otherwise. `create_hypertable` fails outright against a
    table whose PK is just `id` -- found by actually running migrate
    against real TimescaleDB, not from the SQLite-backed tests, which
    never exercise create_hypertable at all.
    """

    __tablename__ = "readings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    river_id: Mapped[str] = mapped_column(String(32), index=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, index=True, default=_utcnow
    )
    temp_c: Mapped[float] = mapped_column(Float)
    dissolved_oxygen_mgl: Mapped[float] = mapped_column(Float)
    ph: Mapped[float] = mapped_column(Float)
    turbidity_fnu: Mapped[float] = mapped_column(Float)


class AlertRow(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    river_id: Mapped[str] = mapped_column(String(32), index=True)
    parameter: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Float)
    baseline_mean: Mapped[float] = mapped_column(Float)
    z_score: Mapped[float] = mapped_column(Float)
    severity: Mapped[str] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(String(512))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=_utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
