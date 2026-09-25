from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import db
import model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Để False nếu dùng allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


PAID_STATUSES = {"Đã thanh toán", "PAID", "DA_THANH_TOAN"} 

@app.get("/api/tuitions/{student_id}", response_model=model.TuitionResponse)
def get_tuition_info(student_id: str, database: Session = Depends(db.get_db)):
    """
    Tra cứu thông tin học phí qua Mã số sinh viên (student_id)
    """
    if not student_id or not student_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã số sinh viên không hợp lệ.",
        )

    # Sử dụng database.query thay vì db.session.query
    tuition_record = (
        database.query(model.TuitionTable)
        .filter(model.TuitionTable.student_id == student_id)
        .first()
    )

    if not tuition_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sinh viên với MSSV này hoặc không có nợ học phí.",
        )

    # Ràng buộc nghiệp vụ: Không cho thanh toán nếu đã đóng
    if tuition_record.status_ in PAID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Khoản học phí này đã được thanh toán hoàn tất.",
        )
    return tuition_record


@app.put("/api/tuitions/{student_id}/status")
def update_tuition_status(
    student_id: str,
    request: model.TuitionStatusUpdate,
    database: Session = Depends(db.get_db),
):
    """
    Cập nhật trạng thái học phí của sinh viên (Có xử lý Concurrency)
    """
    tuition_record = (
        database.query(model.TuitionTable)
        .filter(model.TuitionTable.student_id == student_id)
        .first()
    )

    if not tuition_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sinh viên với MSSV này.",
        )
        
    # 1. Chặn sớm nếu học phí đã được thanh toán
    if tuition_record.status_ == "Đã thanh toán":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Khoản học phí này đã được thanh toán."
        )

    # 2. Xử lý đồng thời (Concurrency) bằng Optimistic Locking
    updated_rows = database.query(model.TuitionTable).filter(
        model.TuitionTable.student_id == student_id,
        model.TuitionTable.version == tuition_record.version  # Khóa lạc quan: Đảm bảo version chưa bị đổi
    ).update({
        "status_": request.status_,
        "version": tuition_record.version + 1                 # Tăng version lên 1
    })

    # 3. Kiểm tra xem database có cho phép cập nhật không
    if updated_rows == 0:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lỗi đồng thời: Khoản học phí này vừa được một người khác thanh toán thành công."
        )

    database.commit()
    database.refresh(tuition_record)

    return tuition_record
