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

DB_CONNECT_ARGS = {
    'detect_types': sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
}


class _Base(object):
    def __eq__(self, other):
        for k in self.__table__.columns.keys():
            try:
                if getattr(self, k) != getattr(other, k):
                    return False
            except AttributeError:
                return False
        return True

    def __str__(self):
        fields = ('%s="%s"' % (k, v) for k, v in self.__dict__.items()
                  if not k.startswith('_'))
        return "<%s[%s]>" % (self.__class__.__name__, ', '.join(fields))

    def __repr__(self):
        fields = ('%s="%r"' % (k, v) for k, v in self.__dict__.items()
                  if not k.startswith('_'))
        return "<%s[%s]>" % (self.__class__.__name__, ', '.join(fields))


Base = declarative_base(cls=_Base)


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
