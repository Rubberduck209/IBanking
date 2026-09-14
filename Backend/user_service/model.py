from sqlalchemy import Column, Integer, String, Numeric
from pydantic import BaseModel
from db import Base, ENGINE
from decimal import Decimal


class UserTable(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(30))
    email = Column(String(255))
    available_balance = Column(Numeric(15, 2), default=0.00)
    version = Column(Integer, default=1)


class UserLogin(BaseModel):
    username: str
    password: str



class PayerInfo(BaseModel):
    full_name: str
    phone_number: str
    available_balance: Decimal
    email: str | None = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


def main():
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main()
