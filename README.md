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

*   A Debian/Ubuntu based server.
*   Root or sudo privileges.
*   Internet connection to download the script and packages.
*   `curl` and `git` (the script will attempt to install them if missing, but it's good to have them).

### Quick Installation (Debian/Ubuntu)

For a fast setup of the backend on a fresh Debian/Ubuntu server, you can use the following command. This will download and execute the `install.sh` script from the repository.

**Important:**
*   Review the `install.sh` script from the repository if you have security concerns before running it directly.
*   **You MUST replace `YOUR_GIT_REPO_URL_HERE` inside the `install.sh` script (if you download it manually first) OR ensure the script fetched from the URL below is correctly pointing to your desired repository for cloning.** The command below fetches and runs the script as-is from the repository.

```bash
bash <(curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/YOUR_BRANCH_NAME/install.sh)
```
**Note:** Replace `https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/YOUR_BRANCH_NAME/install.sh` with the actual raw URL to the `install.sh` script in your repository (e.g., on your main branch).

After the script finishes, it will guide you through creating a superuser. The backend will be set up with SQLite.

### Detailed Backend Setup (`backend/`)

If you prefer a manual setup or are using a non-Debian/Ubuntu system, follow these steps. The quick installation script automates most of these for Debian/Ubuntu.

**Recommended Method (using installation script manually for Debian/Ubuntu):**

1.  **Clone the repository or download `install.sh`:**
    ```bash
    git clone YOUR_GIT_REPO_URL_HERE xui_customer_panel
    cd xui_customer_panel
    # Ensure install.sh is present
    ```
    Or download `install.sh` manually.
2.  **Edit the script (IMPORTANT if cloned/downloaded manually):**
    *   Open `install.sh` and **replace `YOUR_GIT_REPO_URL_HERE`** with the actual URL of your Git repository if the script itself needs to clone (the quick install command above implies the script is already in the repo being cloned by the script).
3.  **Make the script executable:**
    ```bash
    chmod +x install.sh
    ```
4.  **Run the script:**
    ```bash
    ./install.sh
    ```
    The script will guide you through installing prerequisites, cloning the project (if configured to do so), setting up the Python environment, installing dependencies, running database migrations (for SQLite), and creating a superuser.

**Manual Setup (All Systems - if not using the script):**

1.  **Clone the repository (if not done already):**
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
5.  **Review `backend/project_name/settings.py`:**
    *   The project is now configured to use SQLite (`db.sqlite3` will be created in the `backend/` directory).
    *   Ensure `SECRET_KEY` is strong and unique if deploying.
    *   For production, set `DEBUG = False` and configure `ALLOWED_HOSTS` appropriately.
6.  **Apply database migrations:**
    ```bash
    python manage.py makemigrations panel_app
    python manage.py migrate
    ```
7.  **Create a superuser (admin account):**
    ```bash
    python manage.py createsuperuser
    ```
8.  **(Optional) Collect static files for Django Admin:**
    ```bash
    python manage.py collectstatic --noinput
    ```
9.  **Run the development server:**
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```
    For production, use Gunicorn and a web server like Nginx.

### Frontend Setup (`frontend/`)

(Frontend setup remains the same)

1.  **Navigate to the `frontend` directory:** `cd frontend`
2.  **Install JavaScript dependencies:** `npm install` (or `yarn install`)
3.  **Start the frontend development server:** `npm start` (or `yarn start`)

## API Documentation

Accessible via the following endpoints when the backend server is running:

*   **Swagger UI:** `http://localhost:8000/api/v1/schema/swagger-ui/`
*   **ReDoc:** `http://localhost:8000/api/v1/schema/redoc/`
*   **Schema (OpenAPI 3.0 YAML):** `http://localhost:8000/api/v1/schema/`

## Running Tests

### Backend Tests

1.  Navigate to the `backend/` directory.
2.  Ensure your virtual environment is activated.
3.  Run tests: `python manage.py test panel_app`

## Project Structure

```
project_root/
├── backend/            # Django project (SQLite)
├── frontend/           # React project
├── install.sh          # Installation script (Debian/Ubuntu)
├── .gitignore
└── README.md
```

## Important Notes for Production

*   **Database:** For production, PostgreSQL is recommended over SQLite.
*   **DEBUG Mode:** Set `DEBUG = False` in `settings.py`.
*   **SECRET_KEY:** Use a unique, strong `SECRET_KEY`.
*   **Web Server:** Use Gunicorn and Nginx.
*   **HTTPS:** Secure with SSL/TLS certificates.

## Contribution

(Guidelines for contribution can be added here)
```
