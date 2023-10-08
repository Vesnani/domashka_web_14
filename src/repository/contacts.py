from typing import List
from datetime import datetime, timedelta

from fastapi import Depends
from sqlalchemy.sql import extract
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactModel


async def create_contact(body: ContactModel,  current_user: User, db: Session):
    """
    The create_contact function creates a new contact in the database
    :param body: ContactModel: Get the data from the request body
    :param current_user: User: Get the user_id from the current user
    :param db: Session: Access the database
    :return: The newly created contact
    :doc-author: Trelent
    """
    new_contact = Contact(**body.dict(), user_id=current_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


async def get_contacts(limit: int, offset: int, current_user: User, db: Session):
    """
    The get_contacts function returns a list of contacts for the current user
    :param limit: int: Limit the amount of contacts returned
    :param offset: int: Skip the first n rows
    :param current_user: User: Get the current user's id
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(and_(Contact.user_id == current_user.id)).limit(limit).offset(offset).all()
    return contacts


async def get_contact_by_id(contact_id: int, current_user: User, db: Session):
    """
    The get_contact_by_id function returns a contact by its id.
    Args:
    contact_id (int): The id of the contact to be returned.
    current_user (User): The user who is making the request for a specific contact.
    db (Session): A database session object that allows us to query and manipulate data in our database.
    Returns:
    Contact: A single Contact object with an id matching the one passed into this function as an argument
    :param contact_id: int: Get the contact by id
    :param current_user: User: Get the user_id from the current logged in user
    :param db: Session: Create a database session
    :return: The data from the contact table in the database
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).first()
    print("Contacts:", contacts)
    return contacts


async def update_contact(body: ContactModel, contact_id: int, current_user: User, db: Session):
    """
    The update_contact function updates a contact in the database
    :param body: ContactModel: Pass the contact data to be updated
    :param contact_id: int: Identify the contact to update
    :param current_user: User: Get the user_id of the current user
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(contact_id, current_user, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birth_date = body.birth_date
        db.commit()
    return contact


async def remove_contact(contact_id: int, current_user: User, db: Session):
    """
    The remove_contact function removes a contact from the database.
    Args:
    contact_id (int): The id of the contact to be removed.
    current_user (User): The user who is making this request.
    db (Session): A connection to the database for querying and updating data
    :param contact_id: int: Identify the contact to be deleted
    :param current_user: User: Ensure that the user is authorized to delete a contact
    :param db: Session: Pass the database session to the function
    :return: The contact that was removed
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(contact_id, current_user, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(query: str, current_user: User, db: Session):
    """
    The search_contacts function searches for contacts in the database.
    Args:
    query (str): The search term to look for.
    current_user (User): The user who is making the request. This is used to ensure that only a user's own contacts are returned, not all of them!
    db (Session): A connection to our database, which we use to perform queries and retrieve data from it
    :param query: str: Search for a contact in the database
    :param current_user: User: Identify the user that is making the request
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(
        and_(Contact.user_id == current_user.id),
        Contact.first_name.ilike(f"%{query}%") |
        Contact.last_name.ilike(f"%{query}%") |
        Contact.email.ilike(f"%{query}%")
    ).all()
    return contacts


async def get_contacts_birthdays(current_user: User, db: Session):
    """
    The get_contacts_birthdays function returns a list of contacts whose birthdays are within the next 7 days.
    Args:
    current_user (User): The user who is currently logged in.
    db (Session): A database session object to query the database with
    :param current_user: User: Get the current user's id
    :param db: Session: Access the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    today_month = datetime.today().month
    today_day = datetime.today().day
    future_date_month = (datetime.today() + timedelta(days=7)).month
    future_date_day = (datetime.today() + timedelta(days=7)).day

    contacts = db.query(Contact).filter(and_(
        Contact.user_id == current_user.id),
        (extract('month', Contact.birth_date) == today_month) & (extract('day', Contact.birth_date) >= today_day) |
        (extract('month', Contact.birth_date) == future_date_month) & (extract('day', Contact.birth_date) <= future_date_day)
    ).all()
    return contacts













