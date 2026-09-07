import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import db
import model

# Load biến môi trường
load_dotenv()

# Cấu hình JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY chưa được cấu hình trong file .env!")

app = FastAPI(title="User Service - iBanking", version="1.0.0")

# Cấu hình CORS tối ưu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Khi deploy production, hãy sửa thành domain của Frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"], # Hạn chế các method an toàn
    allow_headers=["*"],
)

security = HTTPBearer()

# --- HÀM HỖ TRỢ ---
def create_access_token(username: str, user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    database: Session = Depends(db.get_db)) -> model.UserTable:
    
    # Bóc tách chuỗi token từ credentials
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError: # Bắt gọn mọi lỗi JWT (Expired, Invalid...) bằng class cha
        raise credentials_exception

    user = database.query(model.UserTable).filter(model.UserTable.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản người dùng")
    
    return user

# --- ENDPOINTS (API) ---

@app.post("/login", response_model=model.Token)
async def login_for_access_token(user_data: model.UserLogin, database: Session = Depends(db.get_db)):
    """
    Xác thực người dùng và trả về JWT Token
    """
    user = database.query(model.UserTable).filter(model.UserTable.username == user_data.username).first()
    
    # Gom chung lỗi Username và Password để tránh Hacker dò quét
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sai tên đăng nhập hoặc mật khẩu",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not user:
        raise invalid_credentials_exception

    is_valid_password = bcrypt.checkpw(user_data.password.encode("utf8"), user.password_hash.encode("utf8"))
    if not is_valid_password:
        raise invalid_credentials_exception

    token = create_access_token(user.username, user.user_id)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/me/payer-info", response_model=model.PayerInfo)
async def read_payer_info(current_user: model.UserTable = Depends(get_current_user)):
    """
    Phần 2a: Lấy thông tin người nộp tiền (Profile) thông qua Token
    """
    return current_user

# ... (các code cũ giữ nguyên)

@app.get("/users/me/balance")
async def get_my_balance(current_user: model.UserTable = Depends(get_current_user)):
    """
    API bảo mật: Trả về số dư và thông tin để Payment Service gọi sang.
    Chỉ chủ nhân của Token mới lấy được thông tin của chính mình.
    """
    return {
        "user_id": current_user.user_id,
        "full_name": current_user.full_name,
        "available_balance": current_user.available_balance
    }