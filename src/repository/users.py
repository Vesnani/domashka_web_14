from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session, then returns the user with that email
    :param email: str: Pass the email address to the function
    :param db: Session: Pass a database session to the function
    :return: The first user that matches the email address
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
    Args:
    body (UserModel): The UserModel object containing the information to be added to the database.
    db (Session): The SQLAlchemy Session object used for querying and updating data in the database.
    Returns:
    User: A User object representing a newly created user
    :param body: UserModel: Pass in the user data from the request body
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user
    :param user: User: Identify the user that is being updated
    :param token: str | None: Update the refresh_token field in the database
    :param db: Session: Create a database session
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True
    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url, db) -> User:
    """
    The update_avatar function updates the avatar of a user.
    Args:
    email (str): The email address of the user to update.
    url (str): The URL for the new avatar image.
    db (Session): A database session object used to query and commit changes to users in our database.  This is an SQLAlchemy Session object, not a Flask-SQLAlchemy Session object!  See https://docs.sqlalchemy.org/en/13/orm/session_basics.html#what-does-the-session-do for more information on how this works
    :param email: Find the user in the database
    :param url: Update the avatar of a user
    :param db: Pass the database connection to the function
    :return: The user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
