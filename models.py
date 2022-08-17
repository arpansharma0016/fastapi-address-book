from sqlalchemy import Column, Integer, String
from database import Base

# Database schema for the Table Address
class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(String)
    longitude = Column(String)