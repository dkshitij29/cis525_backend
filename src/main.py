from fastapi import FastAPI, Form, HTTPException, status
from starlette.middleware.cors import CORSMiddleware
import db
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
    success = db.create_user(
        firstname=firstname,
        lastname=lastname,
        email=email,
        password=password
    )
    if success:
        return {"message": f"User '{email}' created successfully."}
    else:
        # Assuming failure is due to a unique constraint violation (email already exists)
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
    success = db.update_customer_field( 
        identifier_value=identifier_value,
        field_to_update=field_to_update,
        new_value=new_value
    )
    if success:
        return {"message": f"Successfully updated '{field_to_update}' for user '{identifier_value}'."}
    else:
        # Assuming failure is due to user not found or invalid field
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Update failed. User '{identifier_value}' not found or field is invalid."
        )


@app.get("/get_customer_details", status_code=status.HTTP_200_OK)
async def GetCustomerDetails(email: str):
    # FIXED: Ensure you are using db1, not db (which was your old file)
    details = db.get_customer_details(
        email=email
    )
    if details:
        return details
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Customer details not found for email '{email}'."
        )


@app.post("/auth", status_code=status.HTTP_200_OK) # ✅ FIXED: Changed from GET to POST
async def AuthUser(email: str = Form(), password: str = Form()):
    customer_id = db.check_user_credentials(
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
    success = db.delete_user(
        email=email
    )
    if success:
        return {"message": f"Successfully deleted user with email '{email}'."}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User deletion failed. No user found with email '{email}'."
        )


@app.post("/save_itinerary", status_code=status.HTTP_201_CREATED) # Changed to 201 Created
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

    success = db.save_itinerary(
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


@app.delete("/delete_itinerary", status_code=status.HTTP_200_OK) # ✅ FIXED: Changed from PUT to DELETE
async def DeleteItinerary(email: str = Form()):
    success = db.delete_itinerary(
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
    data = db.get_all_itineraries(
        email=email
    )
    if data is not None:
        return data
    else:
        # If the database returns None due to an error, raise 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not retrieve itineraries due to an internal database error."
        )



# # def check_user_credentials(email, password) -> int | None: # Signature updated
#     """
#     Checks if a plaintext password matches the stored hash for a given email.
#     Returns the customer_id (int) on success, or None on failure.
#     """
#     mycursor = None
#     try:
#         # Fetch the customer_id AND the password hash
#         sql = "SELECT customer_id, password_hash FROM customers WHERE email = %s" 
#         conn = db_pool.getconn()
#         mycursor = conn.cursor()
#         mycursor.execute(sql, (email,))
#         result = mycursor.fetchone()
        
#         if not result:
#             print(f"Auth Error: No user found with email '{email}'.")
#             return None # Return None on failure

#         # Unpack results: result[0] is customer_id, result[1] is stored_hash
#         customer_id, stored_hash = result[0], result[1] 
        
#         if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
#             print(f"Auth Success: User '{email}' verified. ID: {customer_id}")
#             return customer_id # **Return the ID on success**
#         else:
#             print(f"Auth Error: Invalid password for user '{email}'.")
#             return None

#     except psycopg2.DatabaseError as err:
#         print(f"Database Error during auth: {err}")
#         return None
#     finally:
#         if mycursor:
#             mycursor.close()
#             db_pool.putconn(conn)