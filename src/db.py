import bcrypt
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from postgrest.exceptions import APIError # Import for specific Supabase error handling
from typing import Dict, Any, List


load_dotenv()

url: str = os.environ.get("SUPABASE_URL") 
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise EnvironmentError("SUPABASE_URL or SUPABASE_KEY environment variables not set.")

try:
    supabase: Client = create_client(url, key)
    print("Supabase client initialized.")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    # In a real app, you might want to exit or fail startup here
    supabase = None 




def password_hash_function(pwd: str) -> str:
   """Hashes a plaintext password using bcrypt."""
   salt = bcrypt.gensalt()
   hashed_bytes = bcrypt.hashpw(pwd.encode('utf-8'), salt)
   return hashed_bytes.decode('utf-8')



def check_user_credentials(email: str, password: str) -> int | None:
    """
    Fetches user hash and verifies password. 
    Returns customer_id on success, None otherwise.
    """
    try:

        response = (
            supabase.table("customers")
            .select("customer_id, password_hash") 
            .eq("email", email)
            .limit(1)
            .execute()
        )
        
        if not response.data:
            print(f"Auth Error: No user found with email '{email}'.")
            return None 

        user_data = response.data[0]
        customer_id, stored_hash = user_data['customer_id'], user_data['password_hash']
        

        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print(f"Auth Success: User '{email}' verified. ID: {customer_id}")
            return customer_id 
        else:
            print(f"Auth Error: Invalid password for user '{email}'.")
            return None

    except APIError as err:
        print(f"Supabase API Error during auth: {err.message}")
        return None
    except Exception as err:
        print(f"Unexpected Error during auth: {err}")
        return None

def create_user(firstname: str, lastname: str, email: str, password: str) -> bool:
    """Creates a new user record."""
    password_hash = password_hash_function(password)
    try:
        response = (
            supabase.table("customers")
            .insert({
                "first_name": firstname, 
                "last_name": lastname, 
                "email": email, 
                "password_hash": password_hash
            })
            .execute()
        )
        print(f"User '{email}' created successfully. ID: {response.data[0]['customer_id']}")
        return True
    
    except APIError as err:
        print(f"Supabase API Error creating user: {err.message}")

        return False
    except Exception as err:
        print(f"Unexpected Error creating user: {err}")
        return False

def update_customer_field(identifier_value: str, field_to_update: str, new_value: Any) -> bool:
    """Updates a single field for a user identified by email."""
    allowed_update_fields = ['first_name', 'last_name', 'email', 'password_hash']
    if field_to_update not in allowed_update_fields:
        print(f"Error: Updating the field '{field_to_update}' is not allowed.")
        return False
        
    try:
        update_data = {field_to_update: new_value}
        
        response = (
            supabase.table("customers")
            .update(update_data)
            .eq("email", identifier_value)
            .execute()
        )
        
        if response.count is not None and response.count > 0:
            print(f"Success: Updated '{field_to_update}' for user {identifier_value}.")
            return True
        elif response.data:
            # Fallback check for update response structure
            print(f"Success: Updated '{field_to_update}' for user {identifier_value}.")
            return True
        else:
            print(f"Notice: No user found with email {identifier_value}. Nothing updated.")
            return False

    except APIError as err:
        print(f"Supabase API Error updating field: {err.message}")
        return False
    except Exception as err:
        print(f"Unexpected Error updating field: {err}")
        return False

def get_customer_details(email: str) -> Dict[str, Any] | None:
    """Fetches a customer's non-sensitive details."""
    try:
        response = (
            supabase.table("customers")
            .select("first_name, last_name, email")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        
        if response.data:
            customer_data = response.data[0]
            print("Customer Found:", customer_data)
            return customer_data
        else:
            print("No customer found with that email.")
            return None
        
    except APIError as err:
        print(f"Supabase API Error getting details: {err.message}")
        return None
    except Exception as err:
        print(f"Unexpected Error getting details: {err}")
        return None

def delete_user(email: str) -> bool:
    """Deletes a user record."""
    try:
        response = (
            supabase.table("customers")
            .delete()
            .eq("email", email)
            .execute()
        )
        
        if response.count is not None and response.count > 0:
            print(f"Successfully deleted user with email '{email}'.")
            return True
        else:
            print(f"No user found with email '{email}'. Nothing deleted.")
            return False
            
    except APIError as err:
        print(f"Supabase API Error deleting user: {err.message}")
        return False
    except Exception as err:
        print(f"Unexpected Error deleting user: {err}")
        return False

# --- Itinerary Functions ---

def save_itinerary(email: str, itinerary_name: str, itinerary_data: Dict[str, Any]) -> bool:
    """Saves a new itinerary linked to a customer's email."""
    try:
        # 1. Get customer_id
        response_id = (
            supabase.table("customers")
            .select("customer_id")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        
        if not response_id.data:
            print(f"Error: No user found with email '{email}'. Cannot save itinerary.")
            return False
            
        cid = response_id.data[0]['customer_id']
        
        # 2. Insert itinerary data
        response_itinerary = (
            supabase.table("itineraries")
            .insert({
                "customer_id": cid, 
                "itinerary_name": itinerary_name, 
                "itinerary_data": itinerary_data # Supabase handles dict -> JSONB
            })
            .execute()
        )
        
        new_itinerary_id = response_itinerary.data[0]['itinerary_id']
        print(f"Success: Saved itinerary '{itinerary_name}' (ID: {new_itinerary_id}) for user {email}.")
        return True
            
    except APIError as err:
        print(f"Supabase API Error saving itinerary: {err.message}")
        return False
    except Exception as err:
        print(f"Unexpected Error saving itinerary: {err}")
        return False

def delete_itinerary(email: str) -> bool:
    """Deletes ALL itineraries associated with a user's email."""
    try:
        # 1. Get customer_id
        sql_get_id = (
            supabase.table("customers")
            .select("customer_id")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        
        if not sql_get_id.data:
            print(f"Error: No user found with email '{email}'. Cannot delete itineraries.")
            return False 
        
        customer_id = sql_get_id.data[0]['customer_id']

        # 2. Delete itineraries by customer_id
        response_delete = (
            supabase.table("itineraries")
            .delete()
            .eq("customer_id", customer_id)
            .execute()
        )

        deleted_count = response_delete.count if response_delete.count is not None else len(response_delete.data)
        
        print(f"Success: Deleted {deleted_count} itinerary/itineraries for user '{email}'.")
        return True

    except APIError as err:
        print(f"Supabase API Error deleting itineraries: {err.message}")
        return False
    except Exception as err:
        print(f"Unexpected Error deleting itineraries: {err}")
        return False


def get_all_itineraries(email: str) -> List[Dict[str, Any]] | None:
    """Fetches all itineraries for a given user email using a join."""
    try:
        # Supabase API does the join via foreign key relationship in the 'select' string
        sql_query = (
            supabase.table("itineraries")
            .select("itinerary_id, itinerary_name, itinerary_data, customers!inner(email)")
            .eq("customers.email", email)
            .order("itinerary_id", desc=True)
            .execute()
        )
        
        # The result includes the nested 'customers' field. We extract the core itinerary data.
        itineraries_list = []
        for item in sql_query.data:
            # Clean the data to match the original function's output structure
            clean_item = {
                'itinerary_id': item['itinerary_id'],
                'itinerary_name': item['itinerary_name'],
                'itinerary_data': item['itinerary_data'],
            }
            itineraries_list.append(clean_item)
        
        if itineraries_list:
            print(f"Found {len(itineraries_list)} itineraries for user '{email}'.")
        else:
            print(f"No itineraries found for user '{email}'.")
            
        return itineraries_list

    except APIError as err:
        print(f"Supabase API Error getting all itineraries: {err.message}")
        return None
    except Exception as err:
        print(f"Unexpected Error getting all itineraries: {err}")
        return None