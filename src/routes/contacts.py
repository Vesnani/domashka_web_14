from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=['contacts'])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Get the data from the request body
    :param current_user: User: Get the user id of the current logged in user
    :param db: Session: Pass the database session to the repository layer
    :return: A contactmodel object
    :doc-author: Trelent
    """
    new_contact = await repository_contacts.create_contact(body, current_user, db)
    return new_contact


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=3, seconds=8))])
async def get_contacts(skip: int = 0, limit: int = 100, offset: int = 0, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.
    The function takes in three parameters: skip, limit, and db.
    Skip is the number of records to skip before returning results (defaults to 0).
    Limit is the maximum number of records to return (defaults to 100).
    
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :param offset: int
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(limit, offset, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                            db: Session = Depends(get_db)):
    """
    The get_contact_by_id function returns a contact by its id.
    If the contact does not exist, it raises an HTTPException with status code 404 and detail &quot;Not found&quot;.
    
    
    :param contact_id: int: Define the contact_id as an integer and that it is required
    :param current_user: User: Get the current user from the auth_service
    :param db: Session: Get the database session
    :return: The contact with the given id
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1),
                         current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The update_contact function updates a contact in the database.
    The function takes an id, and a body containing the updated information for that contact.
    It then returns the updated contact
    :param body: ContactModel: Pass the contact data to be updated
    :param contact_id: int: Get the contact_id from the url path, and then pass it to the update_contact function
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A contactmodel object
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(body, contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The remove_contact function removes a contact from the database.
    Args:
    contact_id (int): The id of the contact to be removed.
    current_user (User): The user who is making this request.
    db (Session): A connection to the database, provided by FastAPI's dependency injection system
    :param contact_id: int: Identify the contact to be removed
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(query: str, current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    """
    The search_contacts function searches for contacts in the database
    :param query: str: Search for contacts by name or email
    :param current_user: User: Get the current user from the database
    :param db: Session: Get a database session
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.search_contacts(query, current_user, db)
    return contacts


@router.get("/upcoming-birthdays/", response_model=List[ContactResponse])
async def get_contacts_birthdays(current_user: User = Depends(auth_service.get_current_user),
                                 db: Session = Depends(get_db)):
    """
    The get_contacts_birthdays function returns a list of contacts with birthdays in the current month
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of contacts, which is a list of dicts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts_birthdays(current_user, db)
    return contacts
