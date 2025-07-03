# X-UI Customer Panel

This project is a web-based intermediate panel between users and X-UI panels (supporting both Alireza and 3x-ui/Sanai versions). It provides a customer-facing interface and an admin management section.

## Project Goals

*   **Customer Profile:**
    *   Display a complete list of configurations from various servers.
    *   Show QR codes, client codes, and subscription links for easy copying.
    *   Provide connection tutorials.
    *   Global notification system.
*   **Admin Management:**
    *   **Announcements:** Add/delete announcements (displayed as FAQ on login page).
    *   **Server List:** View, edit, and test connected servers.
    *   **Define New Server:** Add new X-UI servers (Alireza or 3x-ui) with connection testing.
    *   **Define Support User:** Create support staff accounts with system-generated credentials.
    *   **Add Manual Config:** Add subscription links to customer profiles manually.
*   **Advanced Client Search:** Implement fuzzy search for client identifiers (emails) in X-UI panels, as they might not be standard email formats.

## Technology Stack (Initial Proposal)

*   **Backend:** Python / Django
*   **Frontend:** React.js
*   **Database:** PostgreSQL
*   **API Communication:** Django REST Framework

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   Node.js and npm (or yarn) for frontend development.
*   PostgreSQL database server.

### Backend Setup (`backend/`)

1.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On Linux/macOS
    source venv/bin/activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables:**
    *   Rename `.env.example` (if provided, otherwise create `.env`) in the `backend/project_name/` directory.
    *   Update `backend/project_name/settings.py`:
        *   Set your `SECRET_KEY`.
        *   Configure `DATABASES` settings for your PostgreSQL instance (DB name, user, password, host, port).
        *   (Ensure `psycopg2-binary` is in `requirements.txt` for PostgreSQL).
5.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations panel_app
    python manage.py migrate
    ```
6.  **Create a superuser (admin account):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set a username, email (optional), and password.
7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The backend API will typically be available at `http://localhost:8000/`.

### Frontend Setup (`frontend/`)

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```
    (Assuming you are in the project root, otherwise `cd ../frontend` if you are in `backend/`)
2.  **Install JavaScript dependencies:**
    ```bash
    npm install
    # or if you use yarn
    # yarn install
    ```
3.  **Start the frontend development server:**
    ```bash
    npm start
    # or
    # yarn start
    ```
    The frontend application will typically be available at `http://localhost:3000/`.
    It is configured in `frontend/package.json` (`"proxy": "http://localhost:8000"`) to proxy API requests to the backend.

## API Documentation

API documentation is auto-generated using `drf-spectacular` and can be accessed via the following endpoints when the backend server is running:

*   **Swagger UI:** `http://localhost:8000/api/v1/schema/swagger-ui/`
*   **ReDoc:** `http://localhost:8000/api/v1/schema/redoc/`
*   **Schema (OpenAPI 3.0):** `http://localhost:8000/api/v1/schema/`

(Note: These URLs will be active after `drf-spectacular` is configured in the project as part of the documentation step).

## Running Tests

### Backend Tests

1.  Navigate to the `backend/` directory.
2.  Ensure your virtual environment is activated.
3.  Run tests using:
    ```bash
    python manage.py test panel_app
    ```
    To run specific test files or classes:
    ```bash
    python manage.py test panel_app.tests  # For tests.py
    python manage.py test panel_app.test_xui_clients # For test_xui_clients.py
    # python manage.py test panel_app.tests.AuthAndUserManagementTests.test_login_success
    ```

## Project Structure

```
project_root/
├── backend/            # Django project
│   ├── manage.py
│   ├── project_name/   # Main Django project configuration
│   ├── panel_app/      # Our main application logic, models, views, etc.
│   └── requirements.txt
├── frontend/           # React project
│   ├── public/
│   ├── src/
│   └── package.json
├── .gitignore
└── README.md
```

## Next Steps

*   Implement user authentication (customer and admin).
*   Develop API endpoints for X-UI panel interaction.
*   Build out the customer and admin UIs.

## Contribution

(Guidelines for contribution will be added here)
```
