# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from tt.sql import Base


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    timers = relationship("Timer", back_populates="task")


class Timer(Base):
    __tablename__ = 'timer'
    id = Column(Integer, primary_key=True)
    start = Column(DateTime, nullable=False)
    stop = Column(DateTime, nullable=True)

    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    task = relationship("Task", back_populates="timers")

    @property
    def running(self):
        return self.stop is None

    @property
    def elapsed(self):
        if self.running:
            return datetime.utcnow().replace(microsecond=0) - self.start
        else:
            return self.stop - self.start
