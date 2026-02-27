from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.models import User
from app.crud import crud_user


def test_create_user(db_session: Session, client: TestClient):
    response = client.post(
        "/auth/register",
        json={"username": "foo",
              "email": "foo@example.com",
              "password": "123"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "foo"

def test_authenticate_user(db_session: Session, client: TestClient, test_user: User):
    response = client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "123"}
    )
    assert response.status_code == 200

def test_not_authenticate_user(db_session: Session, client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "fake_name", "password": "fake_password"}
    )
    assert response.status_code == 401

def test_user_already_exists(db_session: Session, client: TestClient, test_user: User):
    user = jsonable_encoder(test_user)
    response = client.post(
        "/auth/register",
        json={"username": user["username"],
              "email": user["email"],
              "password": "123"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this nickname already exists"

def test_authenticate_user_wrong_username(db_session: Session, client: TestClient, test_user: User):
    response = client.post(
        "/auth/login",
        data={"username": "wrong_username", "password": "123"}
    )
    assert response.status_code == 401

def test_authenticate_user_wrong_password(db_session: Session, client: TestClient, test_user: User):
    response = client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "wrong_password"}
    )
    assert response.status_code == 401

def test_get_user_by_username(db_session: Session, test_user):
    user = crud_user.get_user_by_username(db_session, test_user.username)
    assert user.username == test_user.username
    assert user.is_active == True

def test_get_nonexisting_user_by_username(db_session: Session):
    user = crud_user.get_user_by_username(db_session, "fake_username")
    assert user is None

def test_get_user_by_id(db_session: Session, test_user):
    user = crud_user.get_user_by_id(db_session, test_user.id)
    assert user.username == test_user.username
    assert user.is_active == True

def test_get_nonexisting_user_by_id(db_session: Session):
    user = crud_user.get_user_by_id(db_session, -1)
    assert user is None