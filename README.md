# API Credit Monitor

This is a FastAPI-based application to monitor OpenAI API usage.  

## Features
- Tracks API usage for users.
- Sends email alerts when usage exceeds limits.
- Scheduled checks via APScheduler.
- MongoDB integration for storing user credits.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Install dependencies: `pip install -r requirements.txt`
3. Add a `.env` file with your OpenAI API key and email credentials.
4. Run the app: `uvicorn app.main:app --reload`

## Note
- `.env` and `venv/` are excluded from version control.
- Make sure to use your own API key in `.env`.
