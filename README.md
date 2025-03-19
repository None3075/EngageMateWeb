# DeustoTech Dashboard Project

## Overview
This Django project is a dashboard application for DeustoTech, featuring data management and visualization capabilities with Grafana integration.

## Prerequisites
- Python 3.x
- Django
- Other dependencies listed in `requirements.txt`
- **Important:** Make sure to have the project [WioMK](https://github.com/mkbaraka/WioMK) running for the embedded Grafana to work

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
python manage.py migrate
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

## Configuration
1. Configure your environment variables in the .env file
2. Install and set up the [WioMK project](https://github.com/mkbaraka/WioMK) for Grafana integration

## Running the Application
```bash
python manage.py runserver
```
Access the application at http://127.0.0.1:8000/

## Project Structure
- dashboardApp - Main dashboard application
  - models.py - Database models including Lecture, WorkHour, etc.
  - views.py - View controllers
  - urls.py - URL routing
  - templates/ - HTML templates
  - static/ - Static assets
- webDeustotech - Secondary application
- Data - CSV data files for import/export

## Usage
1. Log in to the admin interface at http://127.0.0.1:8000/admin/
2. Navigate to the main dashboard

