import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.db.models import Base

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _run_migrations():
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE interaction_logs ADD COLUMN IF NOT EXISTS tecnica VARCHAR"
        ))
        conn.execute(text(
            "ALTER TABLE cuentas ADD COLUMN IF NOT EXISTS limite_diario NUMERIC(12,2) DEFAULT 2000"
        ))
        conn.execute(text(
            "ALTER TABLE transacciones ADD COLUMN IF NOT EXISTS concepto VARCHAR"
        ))
        conn.execute(text(
            "ALTER TABLE transacciones ADD COLUMN IF NOT EXISTS canal_origen VARCHAR"
        ))


def init_db(max_retries: int = 10, delay_seconds: float = 2.0):
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            _run_migrations()
            return
        except OperationalError:
            if attempt == max_retries:
                raise
            time.sleep(delay_seconds)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
