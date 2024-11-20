import asyncio
import os
from enum import StrEnum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, create_engine, update
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import relationship, sessionmaker, Session

MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
DB_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@db:3306/catfeeder?unix_socket=/var/run/mysqld/mysqld.sock"

engine = create_engine(DB_URL)
Base = declarative_base()


class Tables(StrEnum):
    FAMILY = 'family'
    FEEDERS = 'feeders'
    USERS = 'users'
    LOGS = 'logs'
    TAGS = 'tags'
    SCHEDULES = 'schedules'


class DFamily(Base):
    __tablename__ = Tables.FAMILY

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    registered_at = Column(DateTime, index=True)
    logs = relationship("DLog", back_populates="family")


class DUser(Base):
    __tablename__ = Tables.USERS

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, index=True)
    name = Column(String, index=True)
    disabled = Column(Boolean, index=True)
    hashed_password = Column(String, index=True)
    family_id = Column(Integer, ForeignKey(f'{Tables.FAMILY}.id'))
    family_admin = Column(Integer, index=True)
    registered_at = Column(DateTime, index=True)
    logs = relationship("DLog", back_populates="user")


class DFeeder(Base):
    __tablename__ = Tables.FEEDERS

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(Integer, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey(f'{Tables.USERS}.id'))
    tags = relationship("DTag", back_populates="feeder", cascade="all, delete-orphan")
    schedules = relationship("DSchedule", back_populates="feeder", cascade="all, delete-orphan")
    max_meal = Column(Integer)
    current_meal = Column(Integer)
    portion_meal = Column(Integer)
    registered_at = Column(DateTime, index=True)
    logs = relationship("DLog", back_populates="feeder")


class DTag(Base):
    __tablename__ = Tables.TAGS

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feeder_id = Column(Integer, ForeignKey(f'{Tables.FEEDERS}.id'))
    value = Column(String, index=True)
    registered_at = Column(DateTime, index=True)
    feeder = relationship("DFeeder", back_populates="tags")


class DSchedule(Base):
    __tablename__ = Tables.SCHEDULES

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feeder_id = Column(Integer, ForeignKey(f'{Tables.FEEDERS}.id'))
    value = Column(String, index=True)
    registered_at = Column(DateTime, index=True)
    feeder = relationship("DFeeder", back_populates="schedules")


class DLog(Base):
    __tablename__ = Tables.LOGS

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feeder_id = Column(Integer, ForeignKey(f'{Tables.FEEDERS}.id'))
    user_id = Column(Integer, ForeignKey(f'{Tables.USERS}.id'))
    family_id = Column(Integer, ForeignKey(f'{Tables.FAMILY}.id'))
    registered_at = Column(DateTime, index=True)
    feeder = relationship("DFeeder", back_populates="logs")
    user = relationship("DUser", back_populates="logs")
    family = relationship("DFamily", back_populates="logs")


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


fake_users_db = {
    "johndoe@example.com": {
        'user_id': 0,
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2a$10$KSEpyXKj/a0KuV/z8eutQOpE9J6juwowmJO83fUzUp.u3oFdFP8GK",
        "disabled": False,
        "family_id": 0,
        'registration_date': '1970-01-01',

    },
    'vasia@example.com': {
        'user_id': 1,
        "full_name": "Vasia Piatkin",
        "email": "vasia@example.com",
        "hashed_password": "$2a$10$KSEpyXKj/a0KuV/z8eutQOpE9J6juwowmJO83fUzUp.u3oFdFP8GK",
        "disabled": False,
        "family_id": 0,
        'registration_date': '2024-01-01',
    }
}

fake_feeders_db = {
    'johndoe@example.com': {
        228: {
            'feeder_id': 228,
            'name': 'Kitchen',
            'tags': ['tag1'],
            'status': 0.5,
            'schedule': ['09:00', '12:00', '15:00', '18:00', '21:00'],
            'meal': 25
        },
        337: {
            'feeder_id': 337,
            'name': 'MainCoon OGROMNYI',
            'tags': ['tag3', 'tag5'],
            'status': 0.0,
            'schedule': ['09:30', '12:30', '15:30', '18:30', '18:41', '21:30'],
            'meal': 1000
        }
    }
}

fake_families_db = {
    0: {
        'id': 0,
        'name': 'SUPER FAMILY',
        'admin': 0,
    }
}

logs = []
