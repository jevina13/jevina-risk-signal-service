from sqlalchemy import Column, Integer, Float
from database import Base


class Account(Base):
    __tablename__ = 'accounts'
    login = Column(Integer, primary_key=True)
    account_size = Column(Float)
    platform = Column(Integer)
    phase = Column(Integer)
    user_id = Column(Integer)
    challenge_id = Column(Integer)
