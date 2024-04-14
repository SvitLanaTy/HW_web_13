import redis.asyncio as redis
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactResponse
from src.entity.models import User
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/", response_model=list[ContactResponse],
    dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)    
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}")
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.update_contact(body, contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")    
    return contact


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="NO CONTENT")
    return contact
    


@router.get("/search/", response_model=list[ContactResponse])
async def search_contacts(first_name: str = Query(None), last_name: str = Query(None), email: str = Query(None), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.search_contacts(first_name, last_name, email, db, user)
    return contact
    

@router.get("/birthdays/", response_model=list[ContactResponse],
    dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def get_upcoming_birthdays(limit: int = Query(10, ge=10, le=200), offset: int = Query(0, ge=0),
                                db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_upcoming_birthdays(limit, offset, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts
