from sqlalchemy.orm import Session

from tests.utils.users import create_random_user
from tests.utils.posts import create_random_post
from tests.utils.utils import random_lower_string
from app.models.comment import Comment
from app.models.user import User
from app.models.post import Post

def create_random_comment(db_session: Session, user: User = None, post: Post = None):
    if user is None:
        user = create_random_user(db_session)
    if post is None:
        post = create_random_post(db_session)
    post = Comment(
        content=random_lower_string(),
        author_id=user.id,
        post_id=post.id
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post