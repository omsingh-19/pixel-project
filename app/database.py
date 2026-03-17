from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base , sessionmaker
from pathlib import Path

CURRENT_PATH= Path(__file__).resolve().parent.parent
DATABASE_PATH = CURRENT_PATH / 'data'/'vayapar_sarthi_db.db'
SQLALCHEMY_DB_PATH = f'sqlite:///{DATABASE_PATH}'

engine = create_engine(SQLALCHEMY_DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
