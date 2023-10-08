import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy import extract

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    create_contact,
    remove_contact,
    update_contact,
    search_contacts,
    get_contacts_birthdays
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().limit().offset().all.return_value = contacts
        result = await get_contacts(limit=10, offset=0,  current_user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, current_user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await get_contact_by_id(contact_id=1, current_user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(first_name="John", last_name="Doe", email="johndoe@example.com", phone_number="1234567890",
                            birth_date="2000-10-22")
        result = await create_contact(body=body, current_user=self.user, db=self.session)

        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.user_id, self.user.id)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact(self):
        contact = Contact()
        self.session.query().filter_by().first.return_value = contact
        result = await remove_contact(contact_id=1, current_user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter_by().first.return_value = None
        result = await remove_contact(contact_id=1, current_user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact(self):
        body = ContactModel(first_name="John", last_name="Doe", email="johndoe@example.com", phone_number="1234567890",
                            birth_date="2000-10-22")
        contact = Contact(id=1, user_id=1, first_name="OldFirstName", last_name="OldLastName",
                          email="oldemail@example.com", phone_number="9876543210", birth_date="1990-01-01")
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, current_user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birth_date, body.birth_date)

    async def test_update_contact_not_found(self):
        body = ContactModel(first_name="John", last_name="Doe", email="johndoe@example.com", phone_number="1234567890",
                            birth_date="2000-10-22")
        self.session.query().filter_by().first.return_value = None
        result = await update_contact(contact_id=1, body=body, current_user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_search_contacts(self):
        query = "John"
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await search_contacts(query=query, current_user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_birthdays(self):
        today = datetime.today()
        future_date = today + timedelta(days=7)
        self.session.query(Contact).filter(and_(
            Contact.user_id == self.user.id),
            (extract('month', Contact.birth_date) == today.month) &
            (extract('day', Contact.birth_date) >= today.day) |
            (extract('month', Contact.birth_date) == future_date.month) &
            (extract('day', Contact.birth_date) <= future_date.day)
        ).all.return_value = [Contact(), Contact()]
        result = await get_contacts_birthdays(current_user=self.user, db=self.session)
        self.assertEqual(len(result), 2)

    if __name__ == '__main__':
        unittest.main()