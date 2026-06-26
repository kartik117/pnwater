from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from pnwater.storage.orm import AlertRow, ReadingRow


class ReadingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        river_id: str,
        recorded_at: datetime,
        temp_c: float,
        dissolved_oxygen_mgl: float,
        ph: float,
        turbidity_fnu: float,
    ) -> ReadingRow:
        row = ReadingRow(
            river_id=river_id,
            recorded_at=recorded_at,
            temp_c=temp_c,
            dissolved_oxygen_mgl=dissolved_oxygen_mgl,
            ph=ph,
            turbidity_fnu=turbidity_fnu,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def latest_for_river(self, river_id: str) -> ReadingRow | None:
        stmt = (
            select(ReadingRow)
            .where(ReadingRow.river_id == river_id)
            .order_by(ReadingRow.recorded_at.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def latest_all(self) -> list[ReadingRow]:
        # SQLite/Postgres-portable "latest row per river_id": one query
        # per river rather than a window function, since this table is
        # small (10 rivers) and it keeps the query trivially portable.
        from pnwater.rivers import RIVERS

        rows = []
        for river in RIVERS:
            row = self.latest_for_river(river.id)
            if row is not None:
                rows.append(row)
        return rows


class AlertRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        river_id: str,
        parameter: str,
        value: float,
        baseline_mean: float,
        z_score: float,
        severity: str,
        message: str,
        recorded_at: datetime,
    ) -> AlertRow:
        row = AlertRow(
            river_id=river_id,
            parameter=parameter,
            value=value,
            baseline_mean=baseline_mean,
            z_score=z_score,
            severity=severity,
            message=message,
            recorded_at=recorded_at,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def recent(self, limit: int = 50) -> list[AlertRow]:
        stmt = select(AlertRow).order_by(AlertRow.recorded_at.desc()).limit(limit)
        return list(self.session.execute(stmt).scalars().all())
