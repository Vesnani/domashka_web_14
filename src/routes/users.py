from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserModel, UserResponse, TokenModel, UserDb
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings

router = APIRouter(prefix='/users', tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function returns the current user's information.
    tags: [users] # This is a tag that can be used to group operations by resources or any other qualifier.
    summary: Returns the current user's information.
    description: Returns the current user's information based on their JWT token in their request header.
    responses: # The possible responses this operation can return, along with descriptions and examples of each response type (if applicable).
    &quot;200&quot;:  # HTTP status code 200 indicates success! In this case, it means we successfully returned a User
    :param current_user: User: Get the current user from the database
    :return: The current user, which is the user that was authenticated by the auth_service
    :doc-author: Trelent
    """
    return current_user


@router.put("/avatar", response_model=UserDb)
async def update_contact(file: UploadFile = File(), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates the contact information of a user.
    Args:
    file (UploadFile): The avatar image to be uploaded.
    db (Session, optional): SQLAlchemy Session. Defaults to Depend(get_db).
    current_user (User, optional): The currently logged-in user object. Defaults to Depends(auth_service.get_current_user).
    
    :param file: UploadFile: Get the file from the request
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :return: The user object, but the avatar_url is not updated
    :doc-author: Trelent
    """

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    public_id = f"My images/{current_user.username}{current_user.id}"
    cloudinary.uploader.upload(file.file, public_id=public_id, owerwrite=True)
    avatar_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill')
    user = await repository_users.update_avatar(current_user.email, avatar_url, db)

    return user
