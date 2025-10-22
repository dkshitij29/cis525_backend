import psycopg2
from psycopg2.extensions import connection
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from src.db import *

app = FastAPI()
origins = [
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """
    Dependency to get a DB connection per request.
    Ensures the connection is always closed.
    """
    db_conn = get_db_connection()
    if db_conn is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Database connection failed"
        )
    try:
        yield db_conn
    finally:
        db_conn.close() # Close the connection after the request is done

# --- Pydantic Request/Response Models ---
# These models validate incoming data and serialize outgoing data.

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr # Pydantic validates this is a real email format
    password: str

class UserAuth(BaseModel):
    email: EmailStr
    password: str

class UserDetails(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: EmailStr
    # We never return the password hash
    class Config:
        orm_mode = True # Helps map psycopg2 DictCursor to the model

class UserUpdate(BaseModel):
    field_to_update: str
    new_value: str

class ItineraryCreate(BaseModel):
    email: EmailStr
    itinerary_name: str
    itinerary_data: dict # Expecting a JSON object

class ItineraryDetails(BaseModel):
    itinerary_id: int
    itinerary_name: str
    itinerary_data: dict
    class Config:
        orm_mode = True

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "CRUD is working"}

@app.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, db: connection = Depends(get_db)):
    """
    Creates a new user. Passwords are hashed here, not by the client.
    """
    hashed_pw = password_hash_function(user.password)
    
    new_id = create_user(
        mydb=db,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        password_hash=hashed_pw
    )
    
    if new_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to create user. Email may already exist."
        )
    
    return {"customer_id": new_id, "email": user.email, "status": "created"}

@app.put("/update_customer_field")
async def update_customer_field_endpoint(email: EmailStr, update_data: UserUpdate, db: connection = Depends(get_db)):
    """
    Updates a single field for a customer identified by email.
    """
    # Hash the password if that's the field being updated
    value_to_update = update_data.new_value
    if update_data.field_to_update == 'password_hash':
        value_to_update = password_hash_function(update_data.new_value)
        
    success = update_customer_field(
        mydb=db, 
        identifier_value=email,
        field_to_update=update_data.field_to_update,
        new_value=value_to_update
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Failed to update. User '{email}' not found or field '{update_data.field_to_update}' is not allowed."
        )
        
    return {"email": email, "updated_field": update_data.field_to_update, "status": "updated"}

@app.get("/get_customer_details", response_model=UserDetails)
async def get_customer_details_endpoint(email: EmailStr, db: connection = Depends(get_db)):
    """
    Retrieves details for a single customer by email.
    """
    customer = get_customer_details(db, email=email)
    
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Customer not found"
        )
        
    return customer # FastAPI will serialize this using the UserDetails model

@app.post("/auth")
async def auth_user_endpoint(auth_data: UserAuth, db: connection = Depends(get_db)):
    """
    Authenticates a user with email and plaintext password.
    """
    is_valid = check_user_credentials(
        mydb=db,
        email=auth_data.email,
        password=auth_data.password
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
        
    return {"email": auth_data.email, "status": "authenticated"}

@app.delete("/delete_user")
async def delete_user_endpoint(email: EmailStr, db: connection = Depends(get_db)):
    """
    Deletes a user and all their data (cascades) by email.
    """
    success = delete_user(db, email=email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with email '{email}' not found."
        )
        
    return {"email": email, "status": "deleted"}

@app.post("/save_itinerary", status_code=status.HTTP_201_CREATED)
async def save_itinerary_endpoint(itinerary: ItineraryCreate, db: connection = Depends(get_db)):
    """
    Saves a new itinerary for a user.
    """
    success = save_itinerary(
        mydb=db,
        email=itinerary.email,
        itinerary_name=itinerary.itinerary_name,
        itinerary_data=itinerary.itinerary_data
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with email '{itinerary.email}' not found. Cannot save itinerary."
        )
        
    return {"email": itinerary.email, "itinerary_name": itinerary.itinerary_name, "status": "saved"}

@app.delete("/delete_itineraries")
async def delete_itineraries_endpoint(email: EmailStr, db: connection = Depends(get_db)):
    """
    Deletes ALL itineraries for a given user.
    """
    success = delete_itinerary(db, email=email)
    
    if not success:
        # Note: This function might return True even if 0 rows were deleted,
        # as long as the user *exists*. We only raise if the DB call fails.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred while deleting itineraries."
        )
        
    return {"email": email, "status": "itineraries_deleted"}

@app.get("/get_all_itineraries", response_model=List[ItineraryDetails])
async def get_all_itineraries_endpoint(email: EmailStr, db: connection = Depends(get_db)):
    """
    Gets all itineraries for a user, ordered by newest first.
    """
    itineraries = get_all_itineraries(db, email=email)
    
    if itineraries is None:
        # This indicates a database error, not just an empty list
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to retrieve itineraries."
        )
    
    # If 'itineraries' is an empty list, FastAPI handles it correctly
    return itineraries