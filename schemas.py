from pydantic import BaseModel

# Pydantic schema for Address object
class Address(BaseModel):
    latitude: str
    longitude: str