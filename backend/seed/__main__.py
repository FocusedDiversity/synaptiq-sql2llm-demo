"""Entry point: python -m backend.seed"""

import sqlite3
import sys
import os

from backend.seed.create_tables import create_all_tables
from backend.seed.seed_data import seed_all


DB_PATH = os.environ.get("DATABASE_PATH", "data/carwash.db")


def main():
    print(f"Car Wash Database Seeder")
    print(f"Database: {DB_PATH}")
    print("=" * 50)

    # Remove existing DB if present for a clean seed
    if os.path.exists(DB_PATH):
        print(f"Removing existing database: {DB_PATH}")
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        print("Creating tables...")
        create_all_tables(conn)
        print(f"Tables created.\n")

        seed_all(conn)

        print(f"\nDatabase seeded successfully: {DB_PATH}")
    except Exception as e:
        print(f"\nError during seeding: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
