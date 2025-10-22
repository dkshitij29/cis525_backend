### Customer API Endpoints

These endpoints manage user data, including creation, retrieval, and authentication.

* **Create a new customer (Sign Up)**
    * **Method:** `POST`
    * **Endpoint:** `/api/customers`
    * **Description:** Creates a new user record in the `customers` table. The request body would contain the `first_name`, `last_name`, `email`, and `password`. You'd hash the password before saving it.

* **Authenticate a customer (Log In)**
    * **Method:** `POST`
    * **Endpoint:** `/api/auth/login`
    * **Description:** A user submits their `email` and `password`. The server checks the credentials against the database and, if successful, returns an authentication token (like a JWT).

* **Get customer details**
    * **Method:** `GET`
    * **Endpoint:** `/api/customers/{customer_id}`
    * **Description:** Retrieves the profile information for a single customer, identified by their `customer_id`. This is a protected route that would require authentication.

* **Update customer details**
    * **Method:** `PUT` or `PATCH`
    * **Endpoint:** `/api/customers/{customer_id}`
    * **Description:** Updates a customer's information (e.g., `first_name`, `last_name`, or `email`). The request body would contain the fields to be updated.

* **Delete a customer**
    * **Method:** `DELETE`
    * **Endpoint:** `/api/customers/{customer_id}`
    * **Description:** Removes a customer from the database. Due to the `ON DELETE CASCADE` in your `itineraries` table, this would also automatically delete all itineraries associated with that customer.

***

### Itinerary API Endpoints

These endpoints manage the itineraries that belong to a specific customer. Access to these should be protected and only allowed for the logged-in user who owns them.

* **Create a new itinerary**
    * **Method:** `POST`
    * **Endpoint:** `/api/customers/{customer_id}/itineraries`
    * **Description:** Creates a new itinerary for the specified customer. The request body would contain the `itinerary_name` and the `itinerary_data` (JSON).

* **Get all itineraries for a customer**
    * **Method:** `GET`
    * **Endpoint:** `/api/customers/{customer_id}/itineraries`
    * **Description:** Retrieves a list of all itineraries belonging to the specified customer.

* **Get a specific itinerary**
    * **Method:** `GET`
    * **Endpoint:** `/api/itineraries/{itinerary_id}`
    * **Description:** Fetches the details of a single itinerary, identified by its `itinerary_id`.

* **Update an itinerary**
    * **Method:** `PUT` or `PATCH`
    * **Endpoint:** `/api/itineraries/{itinerary_id}`
    * **Description:** Updates an existing itinerary. This could be used to change the name or modify the JSON data for the trip.

* **Delete an itinerary**
    * **Method:** `DELETE`
    * **Endpoint:** `/api/itineraries/{itinerary_id}`
    * **Description:** Deletes a specific itinerary from the database.