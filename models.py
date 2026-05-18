from sqlalchemy import Column, Integer, String, Date
from database import Base

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    competition_type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    organizer = Column(String, nullable=False)
    
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)