from fastapi import FastAPI, Depends
import schemas
import models
from database import engine, SessionLocal
from sqlalchemy.orm import session
import geopy.distance

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

# Validate latitude while creating and updating address
def validate_lat(lat):
    if float(lat) >= -90 and float(lat) <= 90:
        return True
    else: 
        return False

# Validate longitude while creating and updating address
def validate_lon(lon):
    if float(lon) >= -180 and float(lon) <= 180:
        return True
    else: 
        return False

# Get all addresses in the database
@app.get('/address')
def all(db: session = Depends(get_db)):
    addresses = db.query(models.Address).all()
    return addresses


# Create a new address in the database
@app.post('/address')
def create(request: schemas.Address, db: session = Depends(get_db)):

    if not validate_lat(request.latitude):
        return f"Invalid Latitude {request.latitude}"

    if not validate_lon(request.longitude):
        return f"Invalid Longitude {request.longitude}"

    new_address = models.Address(latitude=request.latitude, longitude=request.longitude)
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


# Get a single address from database using Address id
@app.get('/address/{address_id}')
def get_address_by_id(db: session = Depends(get_db), address_id: int = None):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()

    if address:
        return address
    else:
        return f"No address found with id - {address_id}"


# Update the coordinates of an address stored in the database
@app.put('/update-address/{address_id}')
def update_address(request: schemas.Address, db: session = Depends(get_db), address_id: int = None):

    if not validate_lat(request.latitude):
        return f"Invalid Latitude {request.latitude}"

    if not validate_lon(request.longitude):
        return f"Invalid Longitude {request.longitude}"

    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    address.latitude = request.latitude
    address.longitude = request.longitude
    db.commit()
    db.refresh(address)
    return address


# Delete an address from the database
@app.delete('/delete-address/{address_id}')
def delete_address(db: session = Depends(get_db), address_id: int = None):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    
    if address:
        db.delete(address)
        db.commit()
        return "Address Deleted Successfully"
    else:
        return f"No address found with id - {address_id}"


# Get distance between two coordinates
def validate_distance(lat1, lat2, lon1, lon2):
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    return geopy.distance.geodesic(coords_1, coords_2).km
        

# Return addresses in the database to a given coordinates within a given distance in Km
@app.post('/get-address-by-coordinates')
def get_address_by_coords( lat: float, lon: float, dis: float, db: session = Depends(get_db)):
    addresses = db.query(models.Address).all()
    address_list = []
    for address in addresses:
        distance = validate_distance(lat, float(address.latitude), lon, float(address.longitude))
        if distance < dis:
            address_list.append(address)

    return address_list