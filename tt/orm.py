# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy_utc import UtcDateTime
from sqlalchemy.orm import relationship

from tt.sql import Base


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    name = Column(String(24), nullable=False, unique=True)
    description = Column(String(255))
    timers = relationship("Timer", back_populates="task")


class Timer(Base):
    __tablename__ = 'timer'
    id = Column(Integer, primary_key=True)
    start = Column(UtcDateTime(), nullable=False)
    stop = Column(UtcDateTime(), nullable=True)
    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    task = relationship("Task", back_populates="timers")

    @property
    def running(self):
        """True if the timer is currently running."""
        return self.stop is None

    @property
    def elapsed(self):
        """
        A timedelta representing the duration of a completed timer, or
        The current elapsed time for a running timer.
        """
        if self.running:
            return datetime.now(
                timezone.utc).replace(microsecond=0) - self.start
        else:
            return self.stop - self.start
