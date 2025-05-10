# Wellness Tracker

A Django-based web application for tracking daily wellness habits and maintaining a healthy lifestyle.

## Features

- Habit Setup & Daily Log System
- Calendar View of Habit Streaks
- Wellness Score Calculation
- Health Tip Suggestions via API
- Weekly Progress Reports

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd wellness_tracker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root and add:
```
API_NINJAS_KEY=your_api_key_here
```

5. Run migrations:
```bash
python manage.py makemigrations
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

## Usage

1. Access the admin interface at `http://localhost:8000/admin` to manage habits and view data.
2. The main application is available at `http://localhost:8000`.
3. Create habits and log your daily progress.
4. View your progress in the calendar and weekly reports.

## API Integration

The application uses the API Ninjas Health Tips API to fetch daily health tips. You'll need to:
1. Sign up for an API key at https://api-ninjas.com
2. Add your API key to the `.env` file

## Contributing

Feel free to submit issues and enhancement requests! 