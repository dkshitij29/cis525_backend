import psycopg2
import psycopg2.extras
import psycopg2.pool
import bcrypt, json, os
from dotenv import load_dotenv

db_pool = None

def init_db_pool():
    global db_pool
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable not set.")
        return None
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, db_url)
        print("Database connection pool initialized.")
        return db_pool
    except psycopg2.DatabaseError as e:
        print(f"Error initializing connection pool: {e}")
        return None

def password_hash_function(pwd: str) -> str:
   """Hashes a plaintext password using bcrypt."""
   salt = bcrypt.gensalt()
   hashed_bytes = bcrypt.hashpw(pwd.encode('utf-8'), salt)
   return hashed_bytes.decode('utf-8')

def check_user_credentials(  email, password) -> bool:
    """
    Checks if a plaintext password matches the stored hash for a given email.
    """
    mycursor = None
    try:
        sql = "SELECT password_hash FROM customers WHERE email = %s"
        conn = db_pool.getconn()
        mycursor = conn.cursor()
        mycursor.execute(sql, (email,))
        result = mycursor.fetchone()
        
        if not result:
            print(f"Auth Error: No user found with email '{email}'.")
            return False

        stored_hash = result[0]
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print(f"Auth Success: User '{email}' verified.")
            return True
        else:
            print(f"Auth Error: Invalid password for user '{email}'.")
            return False

    except psycopg2.DatabaseError as err:
        print(f"Database Error during auth: {err}")
        return False
    finally:
        if mycursor:
            mycursor.close()
            db_pool.putconn(conn)

def create_user(firstname,lastname,email,password):
    password_hash = password_hash_function(password)
    try:
        sql_query = """INSERT INTO customers 
                            (first_name, last_name, email, password_hash) 
                       VALUES (%s, %s, %s, %s)
                       RETURNING customer_id"""
        
        values = (firstname, lastname, email, password_hash)
        
        conn = db_pool.getconn()
        mycursor = conn.cursor()
        mycursor.execute(sql_query, values)
        conn.commit()
        print(f"User '{email}' created successfully")
        return True
    
    except psycopg2.DatabaseError as err:
        print(f"Error creating user: {err}")
        conn.rollback()
        return None
    finally:
        if mycursor:
            db_pool.putconn(conn)

def update_customer_field(identifier_value, field_to_update, new_value):
    mycursor = None
    conn = db_pool.getconn()
    mycursor = conn.cursor()
    allowed_update_fields = ['first_name', 'last_name', 'email', 'password_hash']
    if field_to_update not in allowed_update_fields:
        print(f"Error: Updating the field '{field_to_update}' is not allowed.")
        return False
    try:

        sql = f"UPDATE customers SET {field_to_update} = %s WHERE email = %s"
        val = (new_value, identifier_value)
        mycursor = conn.cursor()
        mycursor.execute(sql, val)
        conn.commit()
        
        if mycursor.rowcount > 0:
            print(f"Success: Updated '{field_to_update}' for user {identifier_value}.")
            return True
        else:
            print(f"Notice: No user found with email {identifier_value}. Nothing updated.")
            return False

    except psycopg2.DatabaseError as err:
        print(f"Database Error updating field: {err}")
        conn.rollback()
        return False
    finally:
        if mycursor:
            db_pool.putconn(conn)

def get_customer_details(email):
    mycursor = None
    try:
        conn = db_pool.getconn()

        sql = "SELECT first_name, last_name, email FROM customers where email = %s"
        val = (email,)
        
        mycursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        mycursor.execute(sql, val)
        customer_data = mycursor.fetchone()
        
        if customer_data:
            print("Customer Found:", dict(customer_data))
            return customer_data
        else:
            print("No customer found with that email.")
            return None
        
    except psycopg2.DatabaseError as err:
        print(f"Database Error getting details: {err}")
        return None
    finally:
        if mycursor:
            db_pool.putconn(conn)

def delete_user(email):
    mycursor = None
    try:
        conn = db_pool.getconn()
        sql = "DELETE FROM customers WHERE email = %s;"
        val = (email,)
        mycursor = conn.cursor()
        mycursor.execute(sql, val)
        conn.commit()
        
        if mycursor.rowcount > 0:
            print(f"Successfully deleted user with email '{email}'.")
            return True
        else:
            print(f"No user found with email '{email}'. Nothing deleted.")
            return False
            
    except psycopg2.DatabaseError as err:
        print(f"Database Error deleting user: {err}")
        conn.rollback()
        return False
    finally:
        if mycursor:
            db_pool.putconn(conn)

def save_itinerary(email,itinerary_name,itinerary_data):
    mycursor = None
    try:
        conn = db_pool.getconn()   
        mycursor = conn.cursor()        
        sql = "SELECT customer_id FROM customers WHERE email = %s;"
        val = (email,)
        mycursor.execute(sql, val)
        cid = mycursor.fetchone()
        
        if not cid:
            print(f"Error: No user found with email '{email}'. Cannot save itinerary.")
            return False
            
        cid = cid[0]
        
        itinerary_data_json = json.dumps(itinerary_data) 
        
        sql = """INSERT INTO itineraries (customer_id, itinerary_name, itinerary_data) 
                 VALUES (%s, %s, %s)
                 RETURNING itinerary_id;"""
        
        val = (cid, itinerary_name, itinerary_data_json)
        
        mycursor.execute(sql, val)
        new_itinerary_id = mycursor.fetchone()[0]
        conn.commit()
        
        print(f"Success: Saved itinerary '{itinerary_name}' (ID: {new_itinerary_id}) for user {email}.")
        return True
            
    except psycopg2.DatabaseError as err:
        print(f"Database Error saving itinerary: {err}")
        conn.rollback()
        return False
    finally:
        if mycursor:

            db_pool.putconn(conn)

def delete_itinerary(email):
    """
    Deletes ALL itineraries associated with a user's email.
    """
    mycursor = None
    try:
        conn = db_pool.getconn() 
        mycursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        sql_get_id = "SELECT customer_id FROM customers WHERE email = %s"
        mycursor.execute(sql_get_id, (email,))
        result = mycursor.fetchone()

        if not result:
            print(f"Error: No user found with email '{email}'. Cannot delete itineraries.")
            return False 
        
        customer_id = result[0]

        sql_delete = "DELETE FROM itineraries WHERE customer_id = %s"
        mycursor.execute(sql_delete, (customer_id,))

        conn.commit()
        deleted_count = mycursor.rowcount
        
        print(f"Success: Deleted {deleted_count} itinerary/itineraries for user '{email}'.")
        return True

    except psycopg2.DatabaseError as err:
        print(f"Database Error deleting itineraries: {err}")
        conn.rollback()
        return False
    finally:
        if mycursor:

            db_pool.putconn(conn)


def get_all_itineraries(  email):
    mycursor = None
    try:
        conn = db_pool.getconn()
        mycursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql_query = """
            SELECT i.itinerary_id, i.itinerary_name, i.itinerary_data
            FROM itineraries i
            JOIN customers c ON i.customer_id = c.customer_id
            WHERE c.email = %s
            ORDER BY i.itinerary_id DESC; 
        """
        mycursor.execute(sql_query, (email,))
        itineraries_list = mycursor.fetchall()
        
        if itineraries_list:
            print(f"Found {len(itineraries_list)} itineraries for user '{email}'.")
        else:
            print(f"No itineraries found for user '{email}'.")
            
        return itineraries_list 

    except psycopg2.DatabaseError as err:
        print(f"Database Error getting all itineraries: {err}")
        conn.rollback()
        return None 
    finally:
        if mycursor:

            db_pool.putconn(conn)

# print(init_db_pool())
init_db_pool()