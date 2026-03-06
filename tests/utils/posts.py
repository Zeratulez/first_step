from sqlalchemy.orm import Session

from tests.utils.users import create_random_user
from tests.utils.utils import random_lower_string
from app.models.post import Post
from app.models.user import User

def create_random_post(db_session: Session, user: User = None):
    if user is None:
        user = create_random_user(db_session)
    post = Post(
        title=random_lower_string(),
        content=random_lower_string(),
        author_id=user.id
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post