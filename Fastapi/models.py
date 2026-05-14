from sqlalchemy import column,Integer,String,Float
from database import Base
class User(Base):
    __tablename__="Users"
    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True)

    email = Column(String, unique=True)

    password = Column(String)
class Notes(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title=Column(String)
    content=Column(String)
    created_at=
    user_id=Column(Integer)
    

