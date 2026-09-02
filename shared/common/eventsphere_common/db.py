from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def make_engine(env_var: str = "DATABASE_URL"):
    url = os.environ[env_var]
    return create_engine(url, pool_pre_ping=True, future=True)


def make_session_factory(engine) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def get_db_dependency(SessionLocal: sessionmaker):
    """Returns a FastAPI dependency function bound to a given session factory."""

    def _get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return _get_db


@contextmanager
def session_scope(SessionLocal: sessionmaker):
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
