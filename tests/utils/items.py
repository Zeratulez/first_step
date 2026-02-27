import random
import string
from sqlalchemy.orm import Session

from tests.utils.users import create_random_user
from tests.utils.utils import random_lower_string
from app.models import Item


def create_random_item(db_session: Session):
    user = create_random_user(db_session)
    item = Item(
        name=random_lower_string(),
        description=random_lower_string(),
        price=10,
        tax=2.5,
        owner_id=user.id
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item