import os
import logging
import asyncio
from app.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

"""
This script drops and recreates all database tables defined in SQLAlchemy models.
[!] Use with caution: all data will be lost!
"""

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./rdvd.db")

async def recreate_db():
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Connecting to database: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        logging.warning("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        logging.info("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    logging.info("Database recreation complete.")

if __name__ == "__main__":
    print("⚠️ This will DROP and RECREATE all tables in the database!")
    confirm = input("Type 'yes' to continue: ")
    if confirm.strip().lower() == 'yes':
        asyncio.run(recreate_db())
    else:
        print("Aborted.")
