# X-UI Customer Panel (v2.0 - SQLite Backend)

This project is a web-based intermediate panel between users and X-UI panels (supporting both Alireza and 3x-ui/Sanai versions). It provides a customer-facing interface and an admin management section. This version is configured to use SQLite for simpler setup.

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
*   **Advanced Client Search:** Implement fuzzy search for client identifiers (emails) in X-UI panels.

## Technology Stack

*   **Backend:** Python / Django (Configured for SQLite)
*   **Frontend:** React.js
*   **Database:** SQLite (Default for this version)
*   **API Communication:** Django REST Framework
*   **API Documentation:** drf-spectacular (OpenAPI/Swagger)

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   Node.js and npm (or yarn) for frontend development.
*   Git.
*   For Debian/Ubuntu: `build-essential`, `libsqlite3-dev`.

### Backend Setup (`backend/`)

**Recommended Method (using installation script for Debian/Ubuntu):**

1.  **Download the installation script:**
    *   Ensure you have the `install.sh` script in your project root or download it.
2.  **Edit the script:**
    *   Open `install.sh` and **replace `YOUR_GIT_REPO_URL_HERE`** with the actual URL of your Git repository.
3.  **Make the script executable:**
    ```bash
    chmod +x install.sh
    ```
4.  **Run the script:**
    ```bash
    ./install.sh
    ```
    The script will guide you through installing prerequisites, cloning the project, setting up the Python environment, installing dependencies, running database migrations (for SQLite), and creating a superuser.

**Manual Setup (All Systems):**

1.  **Clone the repository (if not done by script):**
    ```bash
    git clone YOUR_GIT_REPO_URL_HERE xui_customer_panel
    # Replace YOUR_GIT_REPO_URL_HERE with your repo URL
    cd xui_customer_panel
    ```
2.  **Navigate to the `backend` directory:**
    ```bash
    cd backend
    ```
3.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On Linux/macOS
    source venv/bin/activate
    ```
4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `psycopg2-binary` is no longer a direct dependency as the default is SQLite. If you switch to PostgreSQL later, you'll need to install it.)*
5.  **Review `backend/project_name/settings.py`:**
    *   The project is now configured to use SQLite (`db.sqlite3` will be created in the `backend/` directory).
    *   Ensure `SECRET_KEY` is strong and unique if deploying (the default is for temporary use).
    *   For production, set `DEBUG = False` and configure `ALLOWED_HOSTS` appropriately.
6.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations panel_app
    python manage.py migrate
    ```
    This will create the `db.sqlite3` file and set up the necessary tables.
7.  **Create a superuser (admin account):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts.
8.  **(Optional) Collect static files for Django Admin:**
    ```bash
    python manage.py collectstatic --noinput
    ```
9.  **Run the development server:**
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```
    The backend API will typically be available at `http://localhost:8000/`. For production, use Gunicorn and a web server like Nginx (see previous deployment guide).

### Frontend Setup (`frontend/`)

(Follow the same steps as previously mentioned for frontend setup - this part is independent of the backend's database choice)

1.  **Navigate to the `frontend` directory:**
    ```bash
    cd frontend
    ```
2.  **Install JavaScript dependencies:**
    ```bash
    npm install
    # or yarn install
    ```
3.  **Start the frontend development server:**
    ```bash
    npm start
    # or yarn start
    ```
    The frontend application will typically be available at `http://localhost:3000/`.
    It is configured in `frontend/package.json` (`"proxy": "http://localhost:8000"`) to proxy API requests to the backend.

## API Documentation

API documentation is auto-generated using `drf-spectacular` and can be accessed via the following endpoints when the backend server is running:

*   **Swagger UI:** `http://localhost:8000/api/v1/schema/swagger-ui/`
*   **ReDoc:** `http://localhost:8000/api/v1/schema/redoc/`
*   **Schema (OpenAPI 3.0 YAML):** `http://localhost:8000/api/v1/schema/`

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
    python manage.py test panel_app.tests  # For tests.py in panel_app
    python manage.py test panel_app.test_xui_clients # For test_xui_clients.py
    ```

## Project Structure

```
project_root/
├── backend/            # Django project (now configured for SQLite)
│   ├── manage.py
│   ├── project_name/   # Main Django project configuration
│   ├── panel_app/      # Our main application logic, models, views, etc.
│   ├── venv/           # Python virtual environment (after setup)
│   ├── db.sqlite3      # SQLite database file (after migrations)
│   └── requirements.txt
├── frontend/           # React project
│   ├── public/
│   ├── src/
│   └── package.json
├── install.sh          # Installation script for backend (Debian/Ubuntu)
├── .gitignore
└── README.md
```

## Important Notes for Production

*   **Database:** While this version uses SQLite for ease of setup, for production environments with higher traffic and concurrency, migrating to a more robust database like PostgreSQL is strongly recommended.
*   **DEBUG Mode:** Always set `DEBUG = False` in `settings.py` for production.
*   **SECRET_KEY:** Use a unique, strong, and secret `SECRET_KEY` in `settings.py`, preferably loaded from an environment variable.
*   **Web Server:** Use a proper WSGI server like Gunicorn and a reverse proxy like Nginx to serve the Django application in production. The Django development server (`manage.py runserver`) is not suitable for production.
*   **HTTPS:** Secure your application with HTTPS using SSL/TLS certificates (e.g., from Let's Encrypt).

## Contribution

(Guidelines for contribution can be added here)
```
