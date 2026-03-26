from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models import User
from tests.utils.posts import create_random_post
from tests.utils.comments import create_random_comment
from app.crud.crud_likes import like_comment, like_post

def test_like_post(db_session: Session, client: TestClient, test_user: User, user_token):
    post = create_random_post(db_session)
    response = client.post(
        f"/posts/{post.id}/like",
        headers=user_token,
    )
    assert response.status_code == 200
    assert len(post.users_likes) >= 1

def test_unlike_post(db_session: Session, client: TestClient, test_user: User, user_token):
    post = create_random_post(db_session)
    like_post(db_session, test_user, post)
    response = client.post(
        f"/posts/{post.id}/like",
        headers=user_token,
    )
    assert response.status_code == 200
    assert len(post.users_likes) == 0

def test_like_comment(db_session: Session, client: TestClient, test_user: User, user_token):
    post = create_random_post(db_session)
    comment = create_random_comment(db_session, post=post)
    response = client.post(
        f"/comments/{comment.id}/like",
        headers=user_token
    )
    assert response.status_code == 200
    assert len(comment.users_likes) >= 1

def test_unlike_comment(db_session: Session, client: TestClient, test_user: User, user_token):
    post = create_random_post(db_session)
    comment = create_random_comment(db_session, post=post)
    like_comment(db_session, test_user, comment)
    response = client.post(
        f"/comments/{comment.id}/like",
        headers=user_token
    )
    assert response.status_code == 200
    assert len(comment.users_likes) == 0