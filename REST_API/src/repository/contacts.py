from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    res = await db.execute(stmt)
    contact = res.scalar_one_or_none()
    if contact:
        return contact
    else:
        return None


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(body: ContactSchema, contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.extra_data = body.extra_data
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    res = await db.execute(stmt)
    contact = res.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
        return contact
    else:
        return None
    

async def search_contacts(first_name: str, last_name: str, email: str, db: AsyncSession, user: User):   
    stmt = None
    if first_name:
        stmt = select(Contact).filter(Contact.first_name.ilike(f"%{first_name}%"), Contact.user == user)
    if last_name:
        stmt = select(Contact).filter(Contact.last_name.ilike(f"%{last_name}%"), Contact.user == user)
    if email:
        stmt = select(Contact).filter(Contact.email.ilike(f"%{email}%"), Contact.user == user)

    contacts = await db.execute(stmt)
    return contacts.scalars().all()


def days_to_birthday(self):
    today = date.today()
    year = today.year if today <= self.replace(year=today.year) else today.year + 1
    end_birthday = self.replace(year=year)
    return (end_birthday - today).days


async def get_upcoming_birthdays(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    results = list(contacts.scalars().all())

    return [contact for contact in results if days_to_birthday(contact.birthday) <= 7]