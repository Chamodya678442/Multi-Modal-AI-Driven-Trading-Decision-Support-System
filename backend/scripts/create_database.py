import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from app.db.session import (
    ADMIN_DATABASE_URL,
    DATABASE_URL,
    POSTGRES_DB,
    Base,
    engine,
)
# Ensure models are imported so SQLAlchemy knows about them
import app.db.models  # noqa: F401


def create_database_if_not_exists():
    """
    Connects to the default PostgreSQL 'postgres' database
    and creates the target database (e.g., 'trading_db') if missing.
    """
    print(f"Checking database '{POSTGRES_DB}'...")
    admin_engine = create_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")

    try:
        with admin_engine.connect() as conn:
            check_query = text(
                f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}';"
            )
            result = conn.execute(check_query).scalar()
            if not result:
                print(f"Creating database '{POSTGRES_DB}'...")
                conn.execute(text(f'CREATE DATABASE "{POSTGRES_DB}";'))
                print(f"Database '{POSTGRES_DB}' created successfully.")
            else:
                print(f"Database '{POSTGRES_DB}' already exists.")
    except Exception as e:
        print(f"Notice during database check: {e}")
        print("Will attempt direct connection to target database...")
    finally:
        admin_engine.dispose()


def create_tables():
    """
    Creates all tables and indexes defined in SQLAlchemy models.
    """
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")


if __name__ == "__main__":
    print("=== INITIALIZING POSTGRESQL DATABASE ===")
    create_database_if_not_exists()
    create_tables()
    print("=== DATABASE INITIALIZATION COMPLETE ===")
