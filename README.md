# FinTrack

FinTrack is a Django-based personal finance tracker built to manage users, accounts, transactions, budgets, savings goals, and gamification badges.

## Features

- User authentication and profiles
- Account management
- Transaction tracking
- Budget categories and budgeting tools
- Savings goals with completion status
- Gamification badges and progress tracking

## Tech stack

- Python
- Django
- PostgreSQL
- HTML/CSS templates

## Local setup

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd FinTrack
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database connection in `FinTrack/settings.py` or use a local settings override.
   The current settings expect PostgreSQL with:
   - NAME: `fintrack_db`
   - USER: `postgres`
   - PASSWORD: `123456`
   - HOST: `127.0.0.1`
   - PORT: `5433`

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```bash
   python manage.py runserver
   ```

## Notes

- `local_settings.py`, `.env`, and other local configuration files are ignored by `.gitignore`.
- If you do not have `requirements.txt`, install Django and any other dependencies manually.
- For production, disable `DEBUG` and configure allowed hosts and secure secrets.
