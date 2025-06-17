# DeustoTech Dashboard Project

## Overview
This Django project is a dashboard application built on top of the project [WioMK](https://github.com/mkbaraka/WioMK), featuring data management and visualization capabilities with a Django Web server.

## Prerequisites
- Python 3.x
- Django
- Other dependencies listed in `requirements.txt`
- **Important:** Make sure to have set up the project [WioMK](https://github.com/None3075/WioMK) running with the correct server IP and set user Tokens for the server to work properly.

## Installation

1. Clone the repository
```bash
git clone https://github.com/None3075/EngageMateWeb.git
cd DjangoProject
```

2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up the database
```bash
python manage.py makemigrations dashboardApp
python manage.py migrate
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

6. Set user Token
Access the Django admin interface at http://127.0.0.1:8000/admin/ and set the user token for the superuser. The user token must be corresponding for that user WioMK user token.

## Other configuration
1. Add your server IP to the ALLOWED_HOSTS in `settings.py` file in the `dashboardApp` directory
2. Install and set up the [WioMK project](https://github.com/None3075/WioMK)

## Running the Application
```bash
python manage.py runserver 0.0.0.0:8000
```
Access the application at http://127.0.0.1:8000/ or from http://[your-ip]:8000/ if you want to access it from other device on the same network.

## Project Structure
- dashboardApp - Main dashboard application
  - models.py - Database models including Lecture, WorkHour, etc.
  - views.py - View controllers
  - urls.py - URL routing
  - templates/ - HTML templates
  - static/ - Static assets
  - Data/ - Directory for CSV data files of each user
- webDeustotech - Secondary application
- Data - CSV data files for import/export

## Usage
1. Log in to the admin interface at http://127.0.0.1:8000/admin/
2. Navigate to the main dashboard

