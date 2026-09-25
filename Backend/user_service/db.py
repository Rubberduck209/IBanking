import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_user = os.getenv("DB_USER", "root")
db_pass = os.getenv("DB_PASS", "")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "3306")
# Phải khớp CHÍNH XÁC (kể cả hoa/thường) với tên DB trong IBankingSQL.sql: `user_DB`
database_name = os.getenv("DB_NAME", "user_DB")

DATABASE = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{database_name}?charset=utf8mb4&use_unicode=1"

ENGINE = create_engine(DATABASE, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
