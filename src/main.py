from fastapi import FastAPI, Form, HTTPException, status
from starlette.middleware.cors import CORSMiddleware
from db import create_user, update_customer_field, get_customer_details, check_user_credentials, delete_user, save_itinerary, delete_itinerary, get_all_itineraries
import json
from typing import Optional


app = FastAPI(title="Web dev backend API")


origins = [
    "http://localhost",
    "http://localhost:3000", # For React (default)
    "http://localhost:5173", 
    "http://localhost:8080", 
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

    
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "CRUD is working"}


@app.post("/create_user", status_code=status.HTTP_201_CREATED)
async def CreateUser(
    firstname: str = Form(),
    lastname: str = Form(),
    email: str = Form(),
    password: str = Form()
):
    success = create_user(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=password
    )
    if success:
        return {"message": f"User '{email}' created successfully."}
    else:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User creation failed. Email or required data may be invalid/duplicate."
        )


@app.put("/update_customer_field", status_code=status.HTTP_200_OK)
async def UpdateCustomerField(
    identifier_value: str = Form(),
    field_to_update: str = Form(),
    new_value: str = Form()
):
    success = update_customer_field( 
        identifier_value=identifier_value,
        field_to_update=field_to_update,
        new_value=new_value
    )
    if success:
        return {"message": f"Successfully updated '{field_to_update}' for user '{identifier_value}'."}
    else:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Update failed. User '{identifier_value}' not found or field is invalid."
        )


@app.get("/get_customer_details", status_code=status.HTTP_200_OK)
async def GetCustomerDetails(email: str):

    details = get_customer_details(
        email=email
    )
    if details:
        return details
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Customer details not found for email '{email}'."
        )


@app.post("/auth", status_code=status.HTTP_200_OK) 
async def AuthUser(email: str = Form(), password: str = Form()):
    customer_id = check_user_credentials(
        email=email,
        password=password
    )
    
    if customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    return {"customer_id": customer_id, "message": "Authentication successful"}


@app.delete("/delete_user", status_code=status.HTTP_200_OK) 
async def DeleteUser(email: str = Form()):
    success = delete_user(
        email=email
    )
    if success:
        return {"message": f"Successfully deleted user with email '{email}'."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User deletion failed. No user found with email '{email}'."
        )


@app.post("/save_itinerary", status_code=status.HTTP_201_CREATED) 
async def SaveItinerary(
    email: str = Form(),
    itinerary_name: str = Form(),
    itinerary_data: str = Form()
):
    try:
        itinerary_data_dict = json.loads(itinerary_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid JSON format for itinerary_data"
        )

    success = save_itinerary(
        email=email,
        itinerary_name=itinerary_name,
        itinerary_data=itinerary_data_dict
    )
    if success:
        return {"message": f"Itinerary '{itinerary_name}' saved successfully."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Failed to save itinerary. Check if user '{email}' exists."
        )


@app.delete("/delete_itinerary", status_code=status.HTTP_200_OK) 
async def DeleteItinerary(email: str = Form()):
    success = delete_itinerary(
        email=email
    )
    if success:
        return {"message": f"Successfully deleted all itineraries for user '{email}'."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Itinerary deletion failed. User '{email}' not found or had no itineraries."
        )


@app.get("/get_all_itineraries", status_code=status.HTTP_200_OK)
async def GetAllItineraries(email: str):
    data = get_all_itineraries(
        email=email
    )
    if data is not None:
        return data
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not retrieve itineraries due to an internal database error."
        )

