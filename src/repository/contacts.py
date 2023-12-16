from sqlalchemy.orm import Session
from sqlalchemy import extract, or_
from typing import Optional
from datetime import datetime, timedelta
from src.database.models import Contact


def create_contact(db: Session, contact_data: dict):
    existing_contact = db.query(Contact).filter(Contact.email == contact_data["email"]).first()
    if existing_contact:
        return None  # або кинути виняток, або повернути існуючий контакт
    new_contact = Contact(**contact_data)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def get_contacts(db: Session, skip: int = 0, limit: int = 10):
    db_contacts = db.query(Contact).offset(skip).limit(limit).all()
    if not db_contacts:
        return None
    return db_contacts


def get_contact(db: Session, contact_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        return None
    return db_contact


def update_contact(db: Session, contact_id: int, updated_data: dict):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        return None
    for key, value in updated_data.items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        return None
    db.delete(db_contact)
    db.commit()
    return db_contact

def search_contacts(db: Session, first_name: Optional[str], last_name: Optional[str], email: Optional[str]):
    query = db.query(Contact)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    results = query.all()
    if not results:
        return None
    return results

# Отримання списку контактів з днями народження на найближчі 7 днів:

def get_upcoming_birthdays(db: Session):
    today = datetime.now().date()
    upcoming = today + timedelta(days=7)

    if today.month == 12 and upcoming.month == 1:
        # Діапазон перетинає кінець року
        end_of_year = db.query(Contact).filter(
            extract('month', Contact.birthday) == 12,
            extract('day', Contact.birthday) >= today.day
        )

        start_of_year = db.query(Contact).filter(
            extract('month', Contact.birthday) == 1,
            extract('day', Contact.birthday) <= upcoming.day
        )

        return end_of_year.union(start_of_year).all()
    elif today.month == upcoming.month:
        # Діапазон у межах одного місяця
        return db.query(Contact).filter(
            extract('month', Contact.birthday) == today.month,
            extract('day', Contact.birthday) >= today.day,
            extract('day', Contact.birthday) <= upcoming.day
        ).all()
    else:
        # Діапазон перетинає місяць, але не рік
        end_of_month = db.query(Contact).filter(
            extract('month', Contact.birthday) == today.month,
            extract('day', Contact.birthday) >= today.day
        )

        start_of_month = db.query(Contact).filter(
            extract('month', Contact.birthday) == upcoming.month,
            extract('day', Contact.birthday) <= upcoming.day
        )

        return end_of_month.union(start_of_month).all()

