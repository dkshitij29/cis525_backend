#!/bin/bash

# --- Configuration ---
BASE_URL="http://localhost:8000"
TEST_EMAIL="curl.test.user@example.com"
TEST_PASSWORD="CurlStrongPassword123!"
TEST_FIRSTNAME="Curl"
TEST_LASTNAME="User"
ITINERARY_DATA='{"day": 1, "city": "Berlin", "activity": "Brandenburg Gate"}'

# --- Utility Functions ---

echo_heading() {
    echo -e "\n=================================================="
    echo -e ">>> $1"
    echo -e "=================================================="
}

# --- Cleanup (Before Test) ---
echo_heading "STEP 0: Pre-Test Cleanup (Attempt to delete user if exists)"
curl -X DELETE "${BASE_URL}/delete_user" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=${TEST_EMAIL}"

# --- 1. Health Check ---
echo_heading "STEP 1: GET / (Root Health Check)"
curl -X GET "${BASE_URL}/"

# --- 2. Create User ---
echo_heading "STEP 2: POST /create_user"
curl -X POST "${BASE_URL}/create_user" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "firstname=${TEST_FIRSTNAME}&lastname=${TEST_LASTNAME}&email=${TEST_EMAIL}&password=${TEST_PASSWORD}"

# --- 3. Authentication ---
echo_heading "STEP 3: POST /auth (Successful Login)"
curl -X POST "${BASE_URL}/auth" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=${TEST_EMAIL}&password=${TEST_PASSWORD}"

# --- 4. Get Details ---
echo_heading "STEP 4: GET /get_customer_details"
curl -X GET "${BASE_URL}/get_customer_details?email=${TEST_EMAIL}"

# --- 5. Update Field ---
echo_heading "STEP 5: PUT /update_customer_field (Change Last Name)"
curl -X PUT "${BASE_URL}/update_customer_field" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "identifier_value=${TEST_EMAIL}&field_to_update=last_name&new_value=UpdatedUser"

# --- 6. Save Itinerary ---
echo_heading "STEP 6: POST /save_itinerary"
# Note: JSON data is passed as a string
curl -X POST "${BASE_URL}/save_itinerary" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=${TEST_EMAIL}&itinerary_name=Berlin%20Trip&itinerary_data=${ITINERARY_DATA}"

# --- 7. Get All Itineraries ---
echo_heading "STEP 7: GET /get_all_itineraries"
curl -X GET "${BASE_URL}/get_all_itineraries?email=${TEST_EMAIL}"

# --- 8. Delete All Itineraries ---
curl -X DELETE "${BASE_URL}/delete_itinerary" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "email=${TEST_EMAIL}"