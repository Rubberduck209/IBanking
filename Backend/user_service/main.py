from fastapi import FastAPI, HTTPException, Depends
import bcrypt
import jwt
import db
import model
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

app = FastAPI()


@app.get("/users", response_model=list[model.UserResponse]) #màn lọc sqlalchemy -> pydantic
def get_users(database: Session = Depends(db.get_db)):
    users = database.query(model.UserTable).all()
    return users

@app.get("/users/{user_id}",response_model=model.UserResponse)
def get_user(user_id:int, database: Session = Depends(db.get_db)):
    user = database.query(model.UserTable).filter(model.UserTable.user_id==user_id).first()
    if not user:
        raise HTTPException(status_code=404,detail="không tìm thấy thông tin người dùng")
    return user

SECRET_KEY = "khoa_bi_mat"

@app.post("/login")
def login(user_data: model.UserLogin, database: Session = Depends(db.get_db)):
    user = database.query(model.UserTable).filter(model.UserTable.username==user_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Sai tên đăng nhập hoặc mật khẩu")
    is_valid = bcrypt.checkpw(
        user_data.password.encode("utf8"), # Mật khẩu người dùng nhập
        user.password_hash.encode("utf8")       # Mật khẩu trong database
    )
    if not is_valid:
        raise HTTPException(status_code=400,detail="Sai tên đăng nhập hoặc mật khẩu")
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "sub": user.username,
        "user_id": user.user_id,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # 5. Trả Token về cho người dùng
    return {"access_token": token, "token_type": "bearer"}