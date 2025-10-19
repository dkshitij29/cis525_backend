import mysql.connector
import bcrypt, json 

def password_hash_function(pwd):
   salt = bcrypt.gensalt()
   hashed_bytes = bcrypt.hashpw(pwd.encode('utf-8'), salt)
   return hashed_bytes.decode('utf-8')

def create_user(mydb,firstname,lastname,email,password_hash):
    mycursor = None
    try:
        #password_hashed = password_hash_function(password_hash)
        sql_query = """INSERT INTO customers 
                            (first_name, last_name, email, password_hash) 
                       VALUES (%s, %s, %s, %s)"""
        values = (firstname, lastname, email, password_hash)
        mycursor = mydb.cursor()
        mycursor.execute(sql_query, values)
        mydb.commit()
        print(f"User '{email}' created successfully with ID: {mycursor.lastrowid}")
        return mycursor.lastrowid
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if mycursor:
            mycursor.close()

def update_customer_field(mydb, identifier_value, field_to_update, new_value):
    mycursor = None
    allowed_update_fields = ['first_name', 'last_name', 'email', 'password_hash']
    if field_to_update not in allowed_update_fields:
        print(f"Error: Updating the field '{field_to_update}' is not allowed.")
        return False
    try:
        sql = f"UPDATE customers SET {field_to_update} = %s WHERE email = %s"
        val = (new_value, identifier_value)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        
        if mycursor.rowcount > 0:
            print(f"Success: Updated '{field_to_update}' for user where email is {identifier_value}.")
            return True
        else:
            print(f"Notice: No user found where {identifier_value} is {identifier_value}. Nothing updated.")
            return False

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        mydb.rollback()
        return False
    finally:
        if mycursor:
            mycursor.close()

def get_customer_details(mydb,email):
    mycursor = None
    try:
        sql = "SELECT * FROM customers where email = %s"
        val = [email,]
        print(type(val))
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(sql, val)
        customer_data = mycursor.fetchone()
        print(customer_data)
        if customer_data:
            print("Customer Found:", customer_data)
            return customer_data
        else:
            print("No customer found with that email.")
            return None
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False
    finally:
        if mycursor:
            mycursor.close()


def auth_user(mydb, email, password_hash):
    mycursor = None
    try:
        sql = "SELECT 1 FROM customers WHERE email = %s AND password_hash = %s"
        val = (email, password_hash)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        result = mycursor.fetchone() # returns a tuple
        if result:
            print("User verified")
            return True
        else:
            print("Check your email and password")
            return False

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False
    finally:
        if mycursor:
            mycursor.close()

def delete_user(mydb, email):
    mycursor = None
    try:
        sql = "DELETE FROM customers WHERE email = %s;"
        val = (email,)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        mydb.commit()
        if mycursor.rowcount > 0:
            print(f"Successfully deleted user with email '{email}' and all their data.")
            return True
        else:
            print(f"No user found with email '{email}'. Nothing deleted.")
            return False
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        # If an error occurs, roll back any partial changes.
        mydb.rollback()
        return False
    finally:
        if mycursor:
            mycursor.close()

def save_iternary(mydb,email,itinerary_name,itinerary_data):
    mycursor = None
    try:
        sql = "SELECT customer_id FROM customers WHERE email = %s;"
        val = (email,)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        cid = mycursor.fetchone()
        if not cid:
            print(f"Error: No user found with email '{email}'. Cannot save itinerary.")
            return False
        cid = cid[0]
        sql = """INSERT INTO itineraries (customer_id, itinerary_name, itinerary_data) VALUES (%s, %s, %s);"""
        val = (cid,itinerary_name,itinerary_data)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        if mycursor.rowcount > 0:
            print(f"Success: Updated '{itinerary_name}' for user where email is {email}.")
            return True
        else:
            print(f"Notice: No user found where email is {email}. Nothing updated.")
            return False
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        mydb.rollback()
        return False
    finally:
        if mycursor:
            mycursor.close()

def delete_iternary(mydb,email):
    # DELETE FROM itineraries WHERE email = %s;
    mycursor = None
    try:
        mycursor = mydb.cursor()

        sql_get_id = "SELECT customer_id FROM customers WHERE email = %s"
        mycursor.execute(sql_get_id, (email,))
        result = mycursor.fetchone()

        if not result:
            print(f"Error: No user found with email '{email}'.")
            return False
        
        customer_id = result[0]

        sql_delete = "DELETE FROM itineraries WHERE customer_id = %s"
        mycursor.execute(sql_delete, (customer_id,))

        mydb.commit()


        deleted_count = mycursor.rowcount
        
        print(f"Success: Deleted {deleted_count} itinerary/itineraries for user '{email}'.")
        return True

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        mydb.rollback()
        return False
    finally:
        if mycursor:
            mycursor.close()


def main():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Iphone@2001",
    database="CIS525"
    )
    print("--- Running Deletion Tests ---")

    # --- Test 1: Success - User has itineraries to delete ---
    # Based on your data, Alice (ID 1) has two itineraries.
    print("\n[Test 1: Deleting itineraries for a user who has them]")
    delete_iternary(mydb, 'bob.j@example.nets')

    # --- Test 2: Success - User exists but has no itineraries ---
    # Based on your data, the user 'test' (ID 5) has no itineraries.
    print("\n[Test 2: Deleting itineraries for a user who has none]")
    delete_iternary(mydb, 'email@riseup.net')

    # --- Test 3: Failure - User does not exist ---
    print("\n[Test 3: Attempting to delete for a non-existent user]")
    delete_iternary(mydb, 'no-one@example.com')

    print("\n--- Tests Complete ---")
    mydb.close()

if __name__ == "__main__":
    main()