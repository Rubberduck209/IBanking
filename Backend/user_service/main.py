from fastapi import FastAPI
import db
import model

app = FastAPI()


@app.get("/users", response_model=list[model.User]) #màn lọc sqlalchemy -> pydantic
def get_users():
    users = db.session.query(model.UserTable).all()
    return users

@app.get("/users/{user_id}",response_model=model.User)
def get_user(user_id:int):
    user = db.session.query(model.UserTable).filter(model.UserTable.user_id==user_id).first()
    return user