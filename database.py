import os
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    BigInteger,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import inspect

Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    x = Column(Integer)
    y = Column(Integer)
    text = Column(String)
    priority = Column(String, default="Low")  # Low, Medium, High, Critical
    timer_enabled = Column(Boolean, default=False)
    timer_time = Column(BigInteger, nullable=True)


# Update the database path
DATABASE_URL = f"sqlite:///{os.path.join('resources', 'notes.db')}"

# Database setup
engine = create_engine(DATABASE_URL)

# Check if the table exists, if not, create it
inspector = inspect(engine)
if not inspector.has_table("notes"):
    Base.metadata.create_all(engine)
else:
    # If the table exists, but doesn't have the 'x' column, recreate the table
    columns = [column['name'] for column in inspector.get_columns('notes')]
    if 'x' not in columns or 'y' not in columns:
        Base.metadata.drop_all(engine)  # Drop the existing table
        # Create the table with the new schema
        Base.metadata.create_all(engine)


# Session setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


session = SessionLocal()