import json
import db


TEST_EMAIL = "test.user.crud.12345@example.com"
TEST_PASSWORD = "myStrongPassword123!"
TEST_FIRSTNAME = "Test"
TEST_LASTNAME = "User"


def run_db_tests():
    """Runs a sequence of tests on the db.py functions."""
    
    print("--- Starting Database Function Test ---")
    
    # if not db.init_db_pool():
    #     print("CRITICAL: Could not connect to database. Aborting tests.")
    #     return
    
    print(f"Successfully connected to database: {not db.init_db_pool()}\n")

    try:

        print(f"STEP 0: Pre-test cleanup for user '{TEST_EMAIL}'...")
        db.delete_user( TEST_EMAIL)
        print("Pre-test cleanup complete.\n")

        # --- TEST 1: HASHING ---
        print("STEP 1: Testing password_hash_function()...")
        hashed_password = db.password_hash_function(TEST_PASSWORD)
        print(f"  > Original password: {TEST_PASSWORD}")
        print(f"  > Hashed password: {hashed_password[:20]}...")
        assert len(hashed_password) > 0
        print("  > SUCCESS: Hashing function works.\n")

        # --- TEST 2: CREATE USER ---
        print(f"STEP 2: Testing create_user() with email '{TEST_EMAIL}'...")
        new_user_id = db.create_user( TEST_FIRSTNAME, TEST_LASTNAME, TEST_EMAIL, hashed_password)
        assert new_user_id is not None
        print(f"  > SUCCESS: User created with ID: {new_user_id}\n")

        # --- TEST 3: AUTHENTICATION (SUCCESS) ---
        print(f"STEP 3: Testing check_user_credentials() (Correct Password)...")
        is_valid = db.check_user_credentials(TEST_EMAIL, TEST_PASSWORD)
        print(f"  > Result: {is_valid}")
        assert is_valid == True
        print("  > SUCCESS: Authentication check passed.\n")

        # --- TEST 4: AUTHENTICATION (FAILURE) ---
        print(f"STEP 4: Testing check_user_credentials() (Incorrect Password)...")
        is_invalid = db.check_user_credentials(TEST_EMAIL, "wrongpassword123")
        print(f"  > Result: {is_invalid}")
        assert is_invalid == False
        print("  > SUCCESS: Authentication check correctly failed.\n")

        # --- TEST 5: GET DETAILS ---
        print(f"STEP 5: Testing get_customer_details()...")
        details = db.get_customer_details(TEST_EMAIL)
        print(f"  > Result: {details}")
        assert details['first_name'] == TEST_FIRSTNAME
        assert 'customer_id' not in details  # Per your recent change
        print("  > SUCCESS: Correct customer details fetched.\n")

        # --- TEST 6: UPDATE FIELD ---
        print(f"STEP 6: Testing update_customer_field()...")
        new_name = "UpdatedFirstName"
        update_success = udb.pdate_customer_field(TEST_EMAIL, "first_name", new_name)
        assert update_success == True
        # Verify the change
        details_updated = db.get_customer_details(TEST_EMAIL)
        print(f"  > Updated details: {details_updated}")
        assert details_updated['first_name'] == new_name
        print("  > SUCCESS: Customer field updated and verified.\n")

        # --- TEST 7: SAVE ITINERARY ---
        print(f"STEP 7: Testing save_itinerary()...")
        itinerary_data_1 = {"day": 1, "city": "Paris", "activity": "Eiffel Tower"}
        itinerary_data_2 = {"day": 1, "city": "Rome", "activity": "Colosseum"}
        
        save_success_1 = db.save_itinerary(TEST_EMAIL, "Paris Trip", itinerary_data_1)
        save_success_2 = db.save_itinerary(TEST_EMAIL, "Rome Trip", itinerary_data_2)
        assert save_success_1 == True
        assert save_success_2 == True
        print("  > SUCCESS: Two itineraries saved.\n")

        # --- TEST 8: GET ALL ITINERARIES ---
        print(f"STEP 8: Testing get_all_itineraries()...")
        all_itineraries = db.get_all_itineraries(TEST_EMAIL)
        print(f"  > Found {len(all_itineraries)} itineraries.")
        assert len(all_itineraries) == 2
        print(f"  > Itinerary 1: {all_itineraries[0]['itinerary_name']}")
        print(f"  > Itinerary 2: {all_itineraries[1]['itinerary_name']}")
        print("  > SUCCESS: Correctly fetched all itineraries.\n")

        # --- TEST 9: DELETE ITINERARIES ---
        print(f"STEP 9: Testing delete_itinerary()...")
        delete_itin_success = db.delete_itinerary(TEST_EMAIL)
        assert delete_itin_success == True
        # Verify deletion
        itineraries_after_delete = db.get_all_itineraries(TEST_EMAIL)
        print(f"  > Itineraries found after delete: {len(itineraries_after_delete)}")
        assert len(itineraries_after_delete) == 0
        print("  > SUCCESS: All itineraries deleted.\n")

    except AssertionError as e:
        print(f"\n--- !!! TEST FAILED !!! ---")
        print(f"Assertion Error: {e}")
        print("--- TEST HALTED ---")
    
    except Exception as e:
        print(f"\n--- !!! UNEXPECTED ERROR !!! ---")
        print(f"Error: {e}")
        print("--- TEST HALTED ---")
        
    finally:
        # --- FINAL CLEANUP ---
        print(f"\nSTEP 10: Final cleanup. Deleting user '{TEST_EMAIL}'...")
        delete_success = db.delete_user(TEST_EMAIL)
        print(f"  > Delete status: {delete_success}")
        
        # Verify final deletion
        final_check = db.get_customer_details(TEST_EMAIL)
        assert final_check is None
        print("  > User successfully deleted.")
        
        if db.init_db_pool():
            db.db_pool.closeall()
            print("\nDatabase connection closed.")
            
        print("--- Test Script Finished ---")

if __name__ == "__main__":
    run_db_tests()