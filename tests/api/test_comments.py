from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models import User
from tests.utils.posts import create_random_post
from tests.utils.comments import create_random_comment

def test_get_post_comments(db_session: Session, client: TestClient):
    post = create_random_post(db_session)
    comment = create_random_comment(db_session, post=post)
    response = client.get(
        f"/posts/{post.id}/comments",
    )
    assert response.status_code == 200
    assert response.json()[0]["content"] == jsonable_encoder(comment)["content"]

def test_create_comment(db_session: Session, client: TestClient, test_user: User, user_token):
    post = create_random_post(db_session, test_user)
    data = {"content": "Some cool comment"}
    response = client.post(
        f"/posts/{post.id}/create_comment",
        headers=user_token,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["content"] == data["content"]
    assert "id" in content
    assert content["author_id"] == test_user.id
    assert content["post_id"] == post.id

def test_create_comment_but_post_not_exist(db_session: Session, client: TestClient, test_user: User, user_token):
    data = {"content": "blablabla"}
    response = client.post(
        "/posts/-1/create_comment",
        headers=user_token,
        json=data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"