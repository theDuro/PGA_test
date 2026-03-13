"""
models.py
SQLAlchemy ORM – definicje tabel i silnik bazy danych.
Używane przez dbclient.py oraz dowolny inny moduł projektu.
"""

import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy.sql import func

# ------------------------------------------------------------------ #
#  Connection URL – brana ze zmiennej środowiskowej lub domyślna      #
# ------------------------------------------------------------------ #
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://pgauser:pgapass@localhost:5432/pga_production",
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ------------------------------------------------------------------ #
#  Base                                                               #
# ------------------------------------------------------------------ #
class Base(DeclarativeBase):
    pass


# ------------------------------------------------------------------ #
#  PARTS                                                              #
# ------------------------------------------------------------------ #
class Part(Base):
    __tablename__ = "parts"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False)

    errors = relationship(
        "Error",
        back_populates="part",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Part id={self.id} name={self.name!r}>"


# ------------------------------------------------------------------ #
#  ERRORS                                                             #
# ------------------------------------------------------------------ #
class Error(Base):
    __tablename__ = "errors"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    code: str = Column(String(64), nullable=False)
    context: str | None = Column(Text, nullable=True)
    part_id: int = Column(Integer, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False)

    part = relationship("Part", back_populates="errors")

    def __repr__(self) -> str:
        return f"<Error id={self.id} code={self.code!r} part_id={self.part_id}>"


# ------------------------------------------------------------------ #
#  CONDITION  (niezależna tabela)                                     #
# ------------------------------------------------------------------ #
class Condition(Base):
    __tablename__ = "condition"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Condition id={self.id} created_at={self.created_at}>"


# ------------------------------------------------------------------ #
#  ML PREDICTIONS                                                     #
# ------------------------------------------------------------------ #
class MlPrediction(Base):
    __tablename__ = "ml_predictions"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    input = Column(JSONB, nullable=False)
    output = Column(JSONB, nullable=False)
    timestamp: str | None = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<MlPrediction id={self.id} created_at={self.created_at}>"


# ------------------------------------------------------------------ #
#  Helper – tworzenie tabel (jeśli nie istnieją)                     #
# ------------------------------------------------------------------ #
def create_tables() -> None:
    """Tworzy wszystkie tabele zdefiniowane w modelu (idempotentne)."""
    Base.metadata.create_all(bind=engine)