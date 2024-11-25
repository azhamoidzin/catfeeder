import asyncio
import datetime
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
    registered_at = Column(DateTime, default=datetime.datetime.now, index=True)
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
    registered_at = Column(DateTime, default=datetime.datetime.now, index=True)
    logs = relationship("DLog", back_populates="user")


class DFeeder(Base):
    __tablename__ = Tables.FEEDERS

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(Integer, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey(f'{Tables.USERS}.id'))
    tags = relationship("DTag", back_populates="feeder", cascade="all, delete-orphan")
    schedule = relationship("DSchedule", back_populates="feeder", cascade="all, delete-orphan")
    max_meal = Column(Integer)
    current_meal = Column(Integer)
    portion_meal = Column(Integer)
    configured = Column(Boolean)
    registered_at = Column(DateTime, default=datetime.datetime.now, index=True)
    logs = relationship("DLog", back_populates="feeder")


class DTag(Base):
    __tablename__ = Tables.TAGS

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feeder_id = Column(Integer, ForeignKey(f'{Tables.FEEDERS}.id'))
    value = Column(String, index=True)
    feeder = relationship("DFeeder", back_populates="tags")


class DSchedule(Base):
    __tablename__ = Tables.SCHEDULES

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feeder_id = Column(Integer, ForeignKey(f'{Tables.FEEDERS}.id'))
    value = Column(String, index=True)
    feeder = relationship("DFeeder", back_populates="schedule")


class DLog(Base):
    __tablename__ = Tables.LOGS

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log = Column(String)
    feeder_id = Column(Integer, ForeignKey(f'{Tables.FEEDERS}.id'))
    user_id = Column(Integer, ForeignKey(f'{Tables.USERS}.id'))
    family_id = Column(Integer, ForeignKey(f'{Tables.FAMILY}.id'))
    meal_poured = Column(Integer)
    registered_at = Column(DateTime, default=datetime.datetime.now, index=True)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
