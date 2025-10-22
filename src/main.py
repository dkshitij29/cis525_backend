from typing import Optional
from fastapi import FastAPI, Form
import psycopg2
import psycopg2.extras
import bcrypt, json, os
from dotenv import load_dotenv
from .db import get_db_connection, create_user, update_customer_field, get_customer_details, check_user_credentials, delete_user, save_itinerary, delete_itinerary, get_all_itineraries

mydb = get_db_connection()
print(mydb)

app = FastAPI()

    
@app.get("/")
async def root():
    return {"message": "CRUD is working"}


@app.post("/create_user")
async def CreateUser(
    firstname: str = Form(),
    lastname: str = Form(),
    email: str = Form(),
    password_hash: str = Form()
):
    return create_user(
        mydb=mydb,
        firstname=firstname,
        lastname=lastname,
        email=email,
        password_hash=password_hash
    )


@app.put("/update_customer_field")
async def UpdateCustomerField(
    identifier_value: str = Form(),
    field_to_update: str = Form(),
    new_value: str = Form()
):
    return update_customer_field(
        mydb=mydb, 
        identifier_value=identifier_value,
        field_to_update=field_to_update,
        new_value=new_value
    )


@app.get("/get_customer_details")
async def GetCustomerDetails(email: str):
    return get_customer_details(
        mydb,
        email=email
    )


@app.get("/auth")
async def AuthUser(email: str, password: str):
    return check_user_credentials(
        mydb,
        email=email,
        password=password
    )


@app.post("/delete_user")
async def DeleteUser(email: str = Form()):
    return delete_user(
        mydb, 
        email=email
    )


@app.post("/save_itinerary")
async def SaveItinerary(
    email: str = Form(),
    itinerary_name: str = Form(),
    itinerary_data: str = Form()
):
    try:
        itinerary_data_dict = json.loads(itinerary_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format for itinerary_data"}

    return save_itinerary(
        mydb=mydb,
        email=email,
        itinerary_name=itinerary_name,
        itinerary_data=itinerary_data_dict
    )


@app.put("/delete_itinerary")
async def DeleteItinerary(email: str = Form()):
    return delete_itinerary(
        mydb=mydb,
        email=email
    )


@app.get("/get_all_itineraries")
async def GetAllItineraries(email: str):
    
    return get_all_itineraries(
        mydb=mydb, 
        email=email
    )
