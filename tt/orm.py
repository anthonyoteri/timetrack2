# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from tt.sql import Base


class Timer(Base):
    __tablename__ = 'timer'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    task_id = Column(
        Integer, ForeignKey('task.id'), nullable=False, unique=True)

    task = relationship("Task", back_populates="timers")

    def __repr__(self):
        return '<Timer(id=%s, task=%s, start_time=%s)>' % (self.id, self.task,
                                                           self.start_time)


class TimeRecord(Base):
    __tablename__ = 'time_record'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    stop_time = Column(DateTime, nullable=False)

    task_id = Column(Integer, ForeignKey('task.id'), nullable=False)
    task = relationship("Task", back_populates="records")

    def __repr__(self):
        return '<TimeRecord(id=%s, task=%s, start_time=%s, stop_time=%s)>' % (
            self.id, self.task, self.start_time, self.stop_time)


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)

    timers = relationship("Timer", back_populates="task")
    records = relationship("TimeRecord", back_populates="task")

    def __repr__(self):
        return "<Task(id={}, name={})>".format(self.id, self.name)
