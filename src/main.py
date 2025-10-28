from fastapi import FastAPI, Form
from starlette.middleware.cors import CORSMiddleware
import db
#from .db import get_db_connection, create_user, update_customer_field, get_customer_details, check_user_credentials, delete_user, save_itinerary, delete_itinerary, get_all_itineraries



app = FastAPI(title="Wed dev backend API")


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

    
@app.get("/")
async def root():
    return {"message": "CRUD is working"}


@app.post("/create_user")
async def CreateUser(
    firstname: str = Form(),
    lastname: str = Form(),
    email: str = Form(),
    password: str = Form()
):
    return db.create_user(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password = password
    )


@app.put("/update_customer_field")
async def UpdateCustomerField(
    identifier_value: str = Form(),
    field_to_update: str = Form(),
    new_value: str = Form()
):
    return db.update_customer_field( 
        identifier_value=identifier_value,
        field_to_update=field_to_update,
        new_value=new_value
    )


@app.get("/get_customer_details")
async def GetCustomerDetails(email: str):
    return db.get_customer_details(
        email=email
    )


@app.get("/auth")
async def AuthUser(email: str, password: str):
    return db.check_user_credentials(
        email=email,
        password=password
    )


@app.post("/delete_user")
async def DeleteUser(email: str = Form()):
    return db.delete_user(
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

    return db.ave_itinerary(
        email=email,
        itinerary_name=itinerary_name,
        itinerary_data=itinerary_data_dict
    )


@app.put("/delete_itinerary")
async def DeleteItinerary(email: str = Form()):
    return db.delete_itinerary(
        email=email
    )


@app.get("/get_all_itineraries")
async def GetAllItineraries(email: str):
    
    return db.get_all_itineraries(
        email=email
    )
