import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Expect a full database URL in the environment, e.g.
# postgres://user:password@host:port/dbname
# or the newer postgresql://
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

# create engine with future flag for SQLAlchemy 2.0 style
engine = create_engine(DATABASE_URL, future=True)


def init_db():
    """Create the predictions table if it doesn't already exist."""
    create_table_sql = text(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            confidence REAL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
    )
    with engine.begin() as conn:
        conn.execute(create_table_sql)


def insert_prediction(name: str, gender: str, confidence: float | None = None):
    """Insert a prediction row into the database."""
    insert_sql = text(
        "INSERT INTO predictions (name, gender, confidence) VALUES (:name, :gender, :confidence)"
    )
    try:
        with engine.begin() as conn:
            conn.execute(insert_sql, {"name": name, "gender": gender, "confidence": confidence})
    except SQLAlchemyError as exc:
        # log error
        print(f"Error inserting prediction: {exc}")


def get_recent_predictions(limit: int = 10) -> list[dict]:
    """Return the most recent prediction rows as a list of dicts."""
    query_sql = text(
        "SELECT id, name, gender, confidence, created_at "
        "FROM predictions ORDER BY created_at DESC LIMIT :limit"
    )
    with engine.connect() as conn:
        result = conn.execute(query_sql, {"limit": limit})
        rows = [dict(row) for row in result]
    return rows
