from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.models.user import User
from app.schemas import user_schema


def get_user_by_username(session: Session, username: str):
    return session.query(User).filter(User.username == username).first()

def create_user(session: Session, user: user_schema.UserCreate, hashed_password: str):
    new_user = User(**user.model_dump(exclude="password"), hashed_password=hashed_password, is_active=True)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def get_user_by_id(session: Session, user_id: int):
    return session.query(User).filter(User.id == user_id).first()

def change_password(
        session: Session,
        user: User,
        hashed_password: str,
):
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Password changed successfully"}

def get_user_by_email(session: Session, email: EmailStr):
    return session.query(User).filter(User.email == email).first()