"""
DB Client – zarządza sesjami SQLAlchemy i operacjami CRUD.
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Part, Error, Condition, create_tables
import csv

# ------------------------------------------------------------------ #
#  Konfiguracja połączenia do PostgreSQL                              #
# ------------------------------------------------------------------ #

DB_USER = "pgauser"
DB_PASSWORD = "pgapass"
DB_HOST = "localhost"       # jeśli aplikacja w tym samym Dockerze, użyj 'pga_database'
DB_PORT = "5432"
DB_NAME = "pga_production"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------------------------------------------------ #
#  Tworzenie tabel (jeśli nie istnieją)                               #
# ------------------------------------------------------------------ #
create_tables()

# ------------------------------------------------------------------ #
#  Context manager dla sesji                                          #
# ------------------------------------------------------------------ #
@contextmanager
def get_session():
    """Zwraca sesję SQLAlchemy i automatycznie ją zamyka po bloku."""
    session = SessionLocal()
    try:
        print("Łączenie z bazą...")
        yield session
        session.commit()
        print("Transakcja zatwierdzona")
    except Exception as e:
        session.rollback()
        print("Błąd w sesji:", e)
        raise
    finally:
        session.close()
        print("Sesja zamknięta")

# ------------------------------------------------------------------ #
#  Funkcje pomocnicze dla CSV                                         #
# ------------------------------------------------------------------ #
def get_line_from_csv(filename, number):
    """
    Wczytuje CSV i zwraca tuple (number, part, text) dla podanego numeru.
    Jeśli numer nie istnieje, zwraca None.
    """
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['number']) == number:
                return (int(row['number']), int(row['part']), row['text'])
    return None

# ------------------------------------------------------------------ #
#  Funkcje CRUD dla tabel                                             #
# ------------------------------------------------------------------ #

# Dodanie nowej części
def add_part(name: str) -> Part:
    with get_session() as session:
        part = Part(name=name)
        session.add(part)
        session.flush()  # żeby od razu mieć ID
        return part

# Pobranie części po ID
def get_part(part_id: int) -> Part | None:
    with get_session() as session:
        return session.query(Part).filter(Part.id == part_id).first()

# Dodanie błędu do części
def add_error(part_id: int, code: str, context: str | None = None) -> Error:
    with get_session() as session:
        error = Error(code=code, context=context, part_id=part_id)
        session.add(error)
        session.flush()
        return error

# Pobranie wszystkich błędów dla części
def get_errors_for_part(part_id: int) -> list[Error]:
    with get_session() as session:
        return session.query(Error).filter(Error.part_id == part_id).all()

# Dodanie warunku
def add_condition() -> Condition:
    with get_session() as session:
        condition = Condition()
        session.add(condition)
        session.flush()
        return condition

# Pobranie wszystkich warunków
def get_all_conditions() -> list[Condition]:
    with get_session() as session:
        return session.query(Condition).all()

# ------------------------------------------------------------------ #
#  Test połączenia (opcjonalnie)                                      #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    with get_session() as session:
        result = session.execute("SELECT 1")
        print("Test połączenia, wynik:", result.scalar())