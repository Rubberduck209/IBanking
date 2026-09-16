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
    Cập nhật trạng thái học phí của sinh viên
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

    tuition_record.status_ = request.status_
    database.commit()
    database.refresh(tuition_record)

    return tuition_record
