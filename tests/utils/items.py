from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item
from tests.utils.users import create_random_user
from tests.utils.utils import random_lower_string


async def create_random_item(db_session: AsyncSession):
    user = await create_random_user(db_session)
    item = Item(
        name=random_lower_string(),
        description=random_lower_string(),
        price=10,
        tax=2.5,
        owner_id=user.id
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item