from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from pydantic import BaseModel
from db import Base, ENGINE
from decimal import Decimal
from datetime import datetime

# --- SQLALCHEMY MODELS (DATABASE) ---

class TransactionTable(Base):
    __tablename__ = 'transactions'
    # Giao dịch thường dùng chuỗi ngẫu nhiên (UUID) làm ID thay vì số tự tăng
    transaction_id = Column(String(255), primary_key=True) 
    user_id = Column(Integer)
    student_id = Column(String(255))
    amount = Column(Numeric(15,2))
    status_ = Column(String(50), default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

class OtpCodeTable(Base):
    __tablename__ = 'otp_codes'
    otp_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(255), ForeignKey('transactions.transaction_id'))
    code_ = Column(String(255))
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)

# --- PYDANTIC SCHEMAS (API) ---

# Schema dùng để nhận yêu cầu tạo giao dịch từ người dùng
class TransactionCreate(BaseModel):
    user_id: int
    student_id: str
    amount: Decimal

# Schema dùng để trả thông tin giao dịch về (không trả các trường thừa)
class TransactionResponse(BaseModel):
    transaction_id: str
    user_id: int
    student_id: str
    amount: Decimal
    status_: str
    created_at: datetime
    
    model_config = {"from_attributes": True}

def main():
    Base.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    main()