from sqlalchemy import Column, Integer, String, Numeric
from pydantic import BaseModel
from db import Base, ENGINE
from decimal import Decimal

# --- SQLALCHEMY MODEL ---
class TuitionTable(Base):
    __tablename__ = 'tuitions'
    student_id = Column(String(255), primary_key=True)
    student_name = Column(String(255))
    tuition_fee_name = Column(String(255))
    amount_due = Column(Numeric(15, 2))
    status_ = Column(String(50))
    version = Column(Integer, default=1)

# --- PYDANTIC SCHEMA ---
class TuitionResponse(BaseModel):
    student_id: str
    student_name: str
    tuition_fee_name: str | None = None
    amount_due: Decimal
    status_: str

    model_config = {"from_attributes": True}

def main():
    Base.metadata.create_all(bind=ENGINE)

if __name__ == "__main__":
    main()