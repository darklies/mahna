#!/bin/bash

# X-UI Customer Panel Installation Script
# Supports Debian/Ubuntu based systems.
# Installs backend with SQLite.

# --- Configuration ---
PROJECT_DIR_NAME="xui_customer_panel" # Name of the directory where the project will be cloned
GIT_REPO_URL="YOUR_GIT_REPO_URL_HERE" # !!! IMPORTANT: Replace this with your actual Git repository URL !!!
# Example: GIT_REPO_URL="https://github.com/username/repository.git"

# --- Helper Functions ---
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

check_command_exists() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 could not be found. Please install it first."
        exit 1
    fi
}

# --- Start Installation ---
print_info "Starting X-UI Customer Panel Backend Installation..."

# 0. Check for Git repository URL
if [ "$GIT_REPO_URL" == "YOUR_GIT_REPO_URL_HERE" ] || [ -z "$GIT_REPO_URL" ]; then
    print_error "Please edit this script and set your GIT_REPO_URL variable."
    exit 1
fi

# 1. Update system packages
print_info "Updating system packages..."
sudo apt-get update -y || { print_error "Failed to update packages."; exit 1; }
# sudo apt-get upgrade -y # Optional: can take a long time

# 2. Install prerequisites
print_info "Installing prerequisites (git, python3, python3-venv, build-essential)..."
sudo apt-get install -y git python3 python3-venv python3-pip build-essential libsqlite3-dev || { print_error "Failed to install prerequisites."; exit 1; }

# 3. Clone the project
if [ -d "$PROJECT_DIR_NAME" ]; then
    print_warning "Directory $PROJECT_DIR_NAME already exists. Skipping clone."
    print_warning "If you want a fresh clone, please remove it first: rm -rf $PROJECT_DIR_NAME"
else
    print_info "Cloning project from $GIT_REPO_URL into $PROJECT_DIR_NAME..."
    git clone "$GIT_REPO_URL" "$PROJECT_DIR_NAME" || { print_error "Failed to clone repository."; exit 1; }
fi

cd "$PROJECT_DIR_NAME/backend" || { print_error "Failed to navigate into project backend directory."; exit 1; }
PROJECT_BACKEND_PATH=$(pwd)
print_info "Project backend located at: $PROJECT_BACKEND_PATH"

# 4. Create and activate virtual environment
print_info "Creating Python virtual environment..."
python3 -m venv venv || { print_error "Failed to create virtual environment."; exit 1; }

print_info "Activating virtual environment..."
source venv/bin/activate || { print_error "Failed to activate virtual environment."; exit 1; }

# 5. Install Python dependencies
print_info "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt || { print_error "Failed to install Python dependencies."; exit 1; }

# 6. Setup Django (collectstatic, migrate, create superuser)
print_info "Running Django collectstatic..."
python manage.py collectstatic --noinput || { print_warning "collectstatic command failed. This might be okay for SQLite dev setup but check for production."; }

print_info "Running Django migrations (this will create db.sqlite3 if it doesn't exist)..."
python manage.py migrate || { print_error "Failed to run Django migrations."; exit 1; }

print_info "Creating Django superuser..."
echo "You will now be prompted to create a superuser account for the Django admin."
python manage.py createsuperuser || { print_error "Failed to create superuser. You can try running 'python manage.py createsuperuser' manually later."; }

# --- Installation Complete ---
print_success "X-UI Customer Panel Backend installation is complete!"
print_info "To run the development server:"
print_info "1. Navigate to the backend directory: cd $PROJECT_BACKEND_PATH"
print_info "2. Activate the virtual environment: source venv/bin/activate"
print_info "3. Run the server: python manage.py runserver 0.0.0.0:8000"
print_warning "Remember that this setup uses SQLite and the Django development server."
print_warning "For a production environment, you should configure Gunicorn and a web server like Nginx, and consider using a more robust database like PostgreSQL."
print_warning "Also, ensure DEBUG=False and a strong SECRET_KEY are set in settings.py for production."

# Deactivate virtual environment if script is sourced, not strictly necessary if executed
# deactivate # This might cause issues depending on how the script is run. Best to let user handle it.

exit 0
