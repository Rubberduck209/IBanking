from sqlalchemy import Column, Integer, String, Numeric
from pydantic import BaseModel
from db import Base
from db import ENGINE
from decimal import Decimal


# userテーブルのモデルUserTableを定義
class UserTable(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(255),nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(30))
    email = Column(String(255))
    available_balance = Column(Numeric(15,2),default=0.00)
    version = Column(Integer,default=1)


class User(BaseModel):
    user_id: int
    username: str
    password_hash: str
    full_name: str
    phone_number: str
    available_balance: Decimal= Decimal('0.00')
    version: int = 1
    
    #Giao tiếp giữa pydantic và sqlalchemy trong khi pydantic đi kiếm kiểu dic user[usename] còn sqlalchemy lại trả về attribute user.usename
    model_config= {"from_attributes": True}


def main():
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main()
