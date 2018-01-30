# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

import contextlib
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import sqlite3

log = logging.getLogger(__name__)
Session = scoped_session(sessionmaker(expire_on_commit=False))
Base = declarative_base()

DB_CONNECT_ARGS = {
    'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
}


def transactional(fn):
    def inner(*args, **kwargs):
        with transaction() as tx:
            fn(tx, *args, **kwargs)

    return inner


@contextlib.contextmanager
def transaction():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        Session.remove()


def connect(db_url='sqlite:///timetrack.db', echo=False):
    log.info("Connecting to database %s", db_url)

    engine = create_engine(
        db_url, connect_args=DB_CONNECT_ARGS, native_datetime=True, echo=echo)
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)
