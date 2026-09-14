import os
import uuid
import random
import smtplib
import asyncio
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import httpx

import db
import model

load_dotenv()



# Cấu hình CORS để Frontend gọi POST không bị lỗi


USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8000")
TUITION_SERVICE_URL = os.getenv("TUITION_SERVICE_URL", "http://127.0.0.1:8001")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

security = HTTPBearer()

async def cleanup_expired_transactions():
    while True:
        try:
            database: Session = next(db.get_db()) #
            now = datetime.now()
            
            exprired_otps = database.query(model.OtpCodeTable).filter(
                model.OtpCodeTable.expires_at < now,
                model.OtpCodeTable.is_used == False
            ).all()
            for otp in exprired_otps:
                otp.is_used = True
                tran = database.query(model.TransactionTable).filter(
                    model.TransactionTable.transaction_id == otp.transaction_id,
                    model.TransactionTable.status_ == "PENDING"
                ).first()
                    
                database.delete(otp)
                database.flush()
                
                if tran:
                    database.delete(tran)
                    
                    print(f"--> Đã tự động hủy giao dịch quá hạn OTP: {tran.transaction_id}")
            database.commit()
            database.close()
        except Exception as e:
            print(f"Lỗi dọn dẹp OTP: {e}")
        
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(cleanup_expired_transactions())
    yield
    task.cancel()

app = FastAPI(title="Payment Service",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def send_otp_email(to_email: str, otp_code: str):
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("Cảnh báo: Chưa cấu hình Email. Bỏ qua bước gửi mail.")
        return
    
    message = MIMEText(f"Mã OTP xác nhận thanh toán học phí của bạn là: {otp_code}. Mã có hiệu lực trong vòng 5 phút.")
    message["Subject"] = "Mã OTP xác thực giao dịch"
    message["From"] = MAIL_USERNAME
    message["To"] = to_email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_USERNAME, to_email, message.as_string())
    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        
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

@app.post("/transactions")
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
            user_response = await client.get(f"{USER_SERVICE_URL}/users/me/payer-info", headers=headers)
            user_bal_response = await client.get(f"{USER_SERVICE_URL}/users/me/balance", headers=headers)
            tuition_response = await client.get(f"{TUITION_SERVICE_URL}/api/tuitions/{tran_data.student_id}")
            
        except httpx.RequestError as e:
            print(f"Lỗi HTTPX: {e}") 
            raise HTTPException(status_code=503, detail="Lỗi kết nối mạng nội bộ")

    #Lỗi User
    if user_response.status_code != 200 or user_bal_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Lỗi xác thực người nộp tiền")
    #Lỗi tuition
    if tuition_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Lỗi hệ thống khi tra cứu học phí")

    user_info = user_response.json()
    user_bal_data = user_bal_response.json()
    
    available_balance = float(user_bal_data["available_balance"])
    auth_user_id = user_bal_data["user_id"]
    amount_due = float(tuition_response.json()["amount_due"])
    requested_amount = float(tran_data.amount)

    if tran_data.user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Lỗi bảo mật: Dữ liệu người nộp tiền không khớp với phiên đăng nhập")
    
    if available_balance < requested_amount:
        raise HTTPException(status_code=400, detail="Số dư khả dụng không đủ để thực hiện giao dịch")
        
    if requested_amount != amount_due:
        raise HTTPException(status_code=400, detail=f"Phải thanh toán toàn bộ học phí ({amount_due} VNĐ). Không hỗ trợ thanh toán một phần.")

    new_tran_id = str(uuid.uuid4()) 
    new_tran = model.TransactionTable(
        transaction_id=new_tran_id,
        user_id=auth_user_id,
        student_id=tran_data.student_id,
        amount=requested_amount,
        status_="PENDING"
    )
    database.add(new_tran)
    database.flush() #DÒNG NÀY ĐỂ ÉP TẠO GIAO DỊCH TRƯỚC (ĐỂ ĐƠ VƯỚNG FOREIN KEY)
    
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.now() + timedelta(minutes=5)
    
    new_otp = model.OtpCodeTable(
        transaction_id=new_tran_id,
        code_=otp_code,
        expires_at=expires_at,
        is_used=False
    )
    database.add(new_otp)
    database.commit()
    
    send_otp_email(user_info.get("email"), otp_code)
    print(f"DEBUG - OTP Code: {otp_code}")
    
    return {"transaction_id": new_tran_id, "status_": "PENDING", "detail": "Mã OTP đã được gửi đến email."}


@app.post("/transactions/verify-otp")
async def verify_transaction_otp(
    verify_data: model.OtpVerifyRequest,
    database: Session = Depends(db.get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            user_bal_response = await client.get(f"{USER_SERVICE_URL}/users/me/balance", headers=headers)
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Lỗi kết nối mạng nội bộ")
        
    if user_bal_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Lỗi xác thực phiên đăng nhập")
    
    auth_user_id = user_bal_response.json()["user_id"]
    
    transaction = database.query(model.TransactionTable).filter(
        model.TransactionTable.transaction_id == verify_data.transaction_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")
        
    # Chặn nếu người nhập OTP không phải là người đã tạo giao dịch này
    if transaction.user_id != auth_user_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xác nhận giao dịch của người khác")
    
    if transaction.status_ != "PENDING":
        raise HTTPException(status_code=400, detail=f"Giao dịch không hợp lệ (Trạng thái: {transaction.status_})")
    
    otp_record = database.query(model.OtpCodeTable).filter(
        model.OtpCodeTable.transaction_id == verify_data.transaction_id
    ).order_by(model.OtpCodeTable.otp_id.desc()).first()
    
    if not otp_record:
        raise HTTPException(status_code=404, detail="Không tìm thấy mã OTP cho giao dịch này")

    if otp_record.is_used:
        raise HTTPException(status_code=400, detail="Mã OTP này đã được sử dụng")

    if datetime.now() > otp_record.expires_at:
        transaction.status_ = "EXPIRED"
        otp_record.is_used = True
        database.commit()
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")

    if otp_record.code_ != verify_data.otp_code:
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác")

    otp_record.is_used = True
    transaction.status_ = "SUCCESS"
    database.commit()

    return {"status": "SUCCESS", "detail": "Xác thực OTP và thanh toán thành công!"}