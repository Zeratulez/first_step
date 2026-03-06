from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models import Post, PostLike, User
from tests.utils.posts import create_random_post
from tests.utils.users import random_user_token

def test_create_post(db_session: Session, client: TestClient, user_token):
    data = {"title": "Testing post", "content": "blablabla"}
    response = client.post(
        "posts/create_post",
        headers=user_token,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert "id" in content
    assert "author_id" in content

def test_get_post(db_session: Session, client: TestClient, test_user: User):
    post = create_random_post(db_session, test_user)
    data = jsonable_encoder(post)
    response = client.get(
        f"/posts/post/{post.id}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert content["id"] == data["id"]
    assert content["author_id"] == data["author_id"]

def test_get_post_not_found(db_session: Session, client: TestClient):
    response = client.get(
        "/posts/post/-1",
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_get_posts(db_session: Session, client: TestClient, test_user: User):
    create_random_post(db_session, test_user)
    create_random_post(db_session, test_user)
    response = client.get(
        "/posts/",
    )
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_update_post(db_session: Session, client: TestClient, test_user: User, user_token):
    post = create_random_post(db_session, test_user)
    data = {"title": "updated title", "content": "Updated content"}
    response = client.patch(
        f"/posts/update/{post.id}",
        headers=user_token,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert content["id"] == post.id
    assert content["author_id"] == test_user.id

def test_update_post_not_author(db_session: Session, client: TestClient):
    post = create_random_post(db_session)
    headers = random_user_token(db_session, client)
    data = {"title": "updated title", "content": "Updated content"}
    response = client.patch(
        f"/posts/update/{post.id}",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the author of the post"

def test_update_post_not_found(db_session: Session, client: TestClient, test_user: User, user_token):
    data = {"title": "updated title", "content": "Updated content"}
    response = client.patch(
        "/posts/update/-1",
        headers=user_token,
        json=data

    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_delete_post(db_session: Session, client: TestClient, test_user: User, user_token):
    post = create_random_post(db_session, test_user)
    response = client.delete(
        f"/posts/delete/{post.id}",
        headers=user_token,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "post deleted"

def test_delete_post_not_found(db_session: Session, client: TestClient, user_token):
    response = client.delete(
        "/posts/delete/-1",
        headers=user_token
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_delete_post_not_author(db_session: Session, client: TestClient, user_token):
    post = create_random_post(db_session)
    response = client.delete(
        f"/posts/delete/{post.id}",
        headers=user_token,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You not the author of the post"