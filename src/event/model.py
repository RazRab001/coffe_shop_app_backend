from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, BigInteger, Double, \
    Boolean, PrimaryKeyConstraint, UUID
from ..database import metadata

event = Table(
    "event",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False),
    Column("description", String),
    Column("is_active", Boolean, default=True)
)

criterion_event = Table(
    "criterion_event",
    metadata,
    Column("event_id", BigInteger, ForeignKey("event.id"), primary_key=True),
    Column("criterion_id", BigInteger, ForeignKey("criterion.id"), primary_key=True),
    PrimaryKeyConstraint("event_id", "criterion_id")
)

benefit_event = Table(
    "benefit_event",
    metadata,
    Column("event_id", BigInteger, ForeignKey("event.id"), primary_key=True),
    Column("benefit_id", BigInteger, ForeignKey("benefit.id"), primary_key=True),
    PrimaryKeyConstraint("event_id", "benefit_id")
)
