from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Machine(Base):
    __tablename__ = "machines"
    id = Column(String, primary_key=True)
    name = Column(String)
    last_seen = Column(Integer)


class Script(Base):
    __tablename__ = "scripts"
    name = Column(String, primary_key=True)
    content = Column(Text)


class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String, ForeignKey("machines.id"))
    script_name = Column(String, ForeignKey("scripts.name"))
    status = Column(String)
    output = Column(Text)
