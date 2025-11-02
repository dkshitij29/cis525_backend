Here are three high-priority issues you can create for your repository, based on our conversation.

---

### **Issue 1: Architectural Flaw: Global database connection crashes app under load**

* **Labels:** `bug`, `critical`, `architecture`
* **Description:**
    The application currently uses a single, global `mydb = get_db_connection()` variable in both `main.py` and `db.py`.

    **Problem:**
    1.  **It will crash:** If this single connection times out or is dropped, the entire application will be dead until it's restarted.
    2.  **It can't scale:** It cannot handle two requests at the same time. The first user will lock the connection, and the second user's request will fail.

    **Task:**
    Refactor the application to use per-request connections managed by FastAPI's dependency injection system.

    **Acceptance Criteria:**
    * [ ] Remove the global `mydb` variable from all files.
    * [ ] Create a `get_db()` generator dependency in `db.py` that `yields` a new connection and `closes` it in a `finally` block.
    * [ ] All API endpoints in `main.py` must use `Depends(get_db)` to get a database connection.
    * [ ] The request-specific `db` connection must be passed to all database functions (e.g., `create_user(mydb=db, ...)`).

---

### **Issue 2: Critical Security: `/auth` endpoint exposes passwords in URL**

* **Labels:** `vulnerability`, `critical`, `security`
* **Description:**
    The `/auth` endpoint is currently a `GET` request that accepts the `password` as a URL query parameter.

    **Problem:**
    This is a severe security vulnerability. It causes plaintext passwords to be saved in server logs, browser history, and network proxy logs, where they can be easily stolen.

    **Task:**
    Change the `/auth` endpoint to a `POST` request and require credentials in the request body.

    **Acceptance Criteria:**
    * [ ] The `@app.get("/auth")` decorator is changed to `@app.post("/auth")`.
    * [ ] The `AuthUser` function signature is changed to accept `email: str = Form()` and `password: str = Form()`.
    * [ ] All client-side code (not in this repo) is updated to send a `POST` request to `/auth` with a form body.

---

### **Issue 3: Critical Security: API lacks authorization, allowing users to access other users' data**

* **Labels:** `vulnerability`, `critical`, `security`, `auth`
* **Description:**
    The application performs *authentication* (checking who a user is) but has zero *authorization* (checking what a user is allowed to do).

    **Problem:**
    Any authenticated user can steal data or delete other users by simply guessing their email. For example, a user can call `/get_all_itineraries?email=someone_else@example.com` and get all of that user's private data. This is known as an **Insecure Direct Object Reference (IDOR)**.

    **Task:**
    Implement token-based (JWT) authentication to secure all endpoints.

    **Acceptance Criteria:**
    * [ ] The `/auth` endpoint, on successful login, generates and returns a **JWT (JSON Web Token)** instead of just `True`.
    * [ ] A new "security dependency" (e.g., `get_current_user`) is created. This function will:
        * Require a JWT in the `Authorization: Bearer <token>` header.
        * Validate the token.
        * Extract the user's email or ID from the token.
        * Raise a 401 Unauthorized error if the token is missing or invalid.
    * [ ] All other endpoints (e.g., `/get_all_itineraries`, `/delete_user`, `/get_customer_details`) are updated to:
        * **Remove** the `email` parameter.
        * **Add** the new security dependency (`Depends(get_current_user)`).
        * Use the user's email *from the token* to query the database.