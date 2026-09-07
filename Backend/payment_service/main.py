import os
import uuid 
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx

import db
import model

load_dotenv()

app = FastAPI(title="Payment Service")

# Cấu hình CORS để Frontend gọi POST không bị lỗi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8000")
TUITION_SERVICE_URL = os.getenv("TUITION_SERVICE_URL", "http://127.0.0.1:8001")

security = HTTPBearer()

@app.get("/transactions", response_model=list[model.TransactionResponse])
def get_transactions(database: Session = Depends(db.get_db)):
    transactions = database.query(model.TransactionTable).all()
    return transactions

@app.get("/transactions/{transaction_id}", response_model=model.TransactionResponse)
def get_transaction(transaction_id: str, database: Session = Depends(db.get_db)):
    transaction = database.query(model.TransactionTable).filter(model.TransactionTable.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")
    return transaction

@app.post("/transactions", response_model=model.TransactionResponse)
async def create_transaction(
    tran_data: model.TransactionCreate, 
    database: Session = Depends(db.get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    
    # Dùng Timeout để chống đơ và truyền Token sang User Service
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            user_response = await client.get(f"{USER_SERVICE_URL}/users/me/balance", headers=headers)
            tuition_response = await client.get(f"{TUITION_SERVICE_URL}/api/tuitions/{tran_data.student_id}")
            
        except httpx.RequestError as e:
            print(f"Lỗi HTTPX: {e}") 
            raise HTTPException(status_code=503, detail="Lỗi kết nối mạng nội bộ giữa các Service")

    # Kiểm tra lỗi từ User Service
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")
    elif user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Lỗi xác thực người nộp tiền")

    # Kiểm tra lỗi từ Tuition Service
    if tuition_response.status_code == 404:
        raise HTTPException(status_code=404, detail="Không tìm thấy khoản nợ học phí của MSSV này")
    elif tuition_response.status_code == 400:
        error_detail = tuition_response.json().get("detail", "Lỗi dữ liệu học phí")
        raise HTTPException(status_code=400, detail=error_detail)
    elif tuition_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Lỗi hệ thống khi tra cứu học phí")

    user_data = user_response.json()
    tuition_data = tuition_response.json()
    
    available_balance = float(user_data["available_balance"])
    amount_due = float(tuition_data["amount_due"])
    requested_amount = float(tran_data.amount)

    if available_balance < requested_amount:
        raise HTTPException(status_code=400, detail="Số dư khả dụng không đủ để thực hiện giao dịch")
        
    if requested_amount != amount_due:
        raise HTTPException(status_code=400, detail=f"Phải thanh toán toàn bộ học phí ({amount_due} VNĐ). Không hỗ trợ thanh toán một phần.")

    new_tran_id = str(uuid.uuid4()) 
    new_tran = model.TransactionTable(
        transaction_id=new_tran_id,
        user_id=tran_data.user_id,
        student_id=tran_data.student_id,
        amount=requested_amount,
        status_="PENDING"
    )
    
    database.add(new_tran)
    database.commit()
    database.refresh(new_tran)
    
    return new_tran