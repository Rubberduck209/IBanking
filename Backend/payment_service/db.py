import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Nạp các biến môi trường từ file .env
load_dotenv()

# Đọc cấu hình từ biến môi trường, có sẵn giá trị mặc định để chống sập
db_user = os.getenv("DB_USER", "root")
db_pass = os.getenv("DB_PASS", "12345678")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "3306")
database_name = os.getenv("DB_NAME", "payment_DB")

# Chuỗi kết nối MySQL chuẩn
DATABASE_URL = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{database_name}?charset=utf8'

ENGINE = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()