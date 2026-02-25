from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas import item_schema, user_schema


def get_items(
        session: Session,
        search: str,
        skip: int,
        limit: int
): 
    query = select(Item).filter(Item.name.contains(search)).offset(skip).limit(limit)
    result = session.scalars(query).all()
    print(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>{result}")
    return result

def create_item(
        session: Session,
        user: user_schema.UserInDB,
        item: item_schema.ItemCreate
):
    new_item = Item(**item.model_dump(), owner_id=user.id)
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    return new_item

def get_item_by_id(session: Session, item_id: int):
    return session.get(Item, item_id)

def update_item(
        session: Session,
        item_db: Item,
        item_data: item_schema.ItemUpdate
):
    for key, value in item_data.model_dump(exclude_unset=True).items():
        setattr(item_db, key, value)
    session.commit()
    session.refresh(item_db)
    return item_db

def delete_item(session: Session, item: Item):
    session.delete(item)
    session.commit()
    return {"message": "item deleted"}
