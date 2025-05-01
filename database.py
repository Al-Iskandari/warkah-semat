from sqlalchemy import Column, Integer, String, Boolean, BigInteger, create_engine
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


# Database setup
engine = create_engine("sqlite:///notes.db")

# Check if the table exists, if not, create it
inspector = inspect(engine)
if not inspector.has_table("notes"):
    Base.metadata.create_all(engine)
else:
    # If the table exists, but doesn't have the 'x' column, recreate the table
    columns = [column['name'] for column in inspector.get_columns('notes')]
    if 'x' not in columns or 'y' not in columns:
        Base.metadata.drop_all(engine)  # Drop the existing table
        Base.metadata.create_all(engine)  # Create the table with the new schema


# Session setup
Session = sessionmaker(bind=engine)
session = Session()