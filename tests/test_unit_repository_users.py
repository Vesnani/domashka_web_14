import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email="johndoe@example.com", db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="johndoe@example.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(username="john_doe", email="johndoe@example.com", password="password")
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))
        self.assertIsNotNone(result.avatar)

    async def test_update_token(self):
        new_token = "new_refresh_token"
        await update_token(user=self.user, token=new_token, db=self.session)
        self.assertEqual(self.user.refresh_token, new_token)
        self.session.commit.assert_called_once()

    async def test_update_token_no_token(self):
        old_token = self.user.refresh_token
        await update_token(user=self.user, token=None, db=self.session)
        self.assertEqual(self.user.refresh_token, old_token)
        self.session.commit.assert_called()

    async def test_confirmed_email(self):
        fake_user = MagicMock()
        self.session.query().filter().first.return_value = fake_user
        await confirmed_email(email="johndoe@example.com", db=self.session)
        self.session.commit.assert_called_once()
        self.assertTrue(fake_user.confirmed)

    async def test_confirmed_email_not_confirmed(self):
        fake_user = MagicMock()
        fake_user.confirmed = False
        self.session.query().filter().first.return_value = fake_user
        result = await confirmed_email(email="johndoe@example.com", db=self.session)
        self.session.commit.assert_called()
        self.assertIsNone(result)

    async def test_update_avatar(self):
        fake_user = MagicMock()
        self.session.query().filter().first.return_value = fake_user
        email = "johndoe@example.com"
        url = "https://example.com/avatar.jpg"
        result = await update_avatar(email=email, url=url, db=self.session)
        self.assertEqual(fake_user.avatar, url)
        self.session.commit.assert_called_once()
        self.assertEqual(result, fake_user)

    async def test_update_avatar_no_avatar(self):
        old_avatar = self.user.avatar
        email = "johndoe@example.com"
        await update_avatar(email=email, url=None, db=self.session)
        self.assertEqual(self.user.avatar, old_avatar)
        self.session.commit.assert_called()
