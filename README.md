# fix_apex - Flask file generation service

This repository contains a Flask app (`app.py`) that accepts an uploaded Excel file and a zip folder, processes them using `input_file_generation.py`, and returns a generated Excel file.

Ready-for-Render deployment files included:
- `requirements.txt` — Python dependencies
- `Procfile` — start command for gunicorn
- `runtime.txt` — Python runtime
- `.gitignore` — ignores generated/test files

Quick local run (development):

1. Create a virtualenv and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Start the app (development server):

```bash
python app.py
```

3. Or run with gunicorn (closer to production):

```bash
gunicorn app:app --bind 0.0.0.0:8000
```

Healthcheck:

```bash
curl http://localhost:5001/health
```

How to deploy to Render (quick):

1. Push this repo to GitHub.
2. In Render dashboard, create a new Web Service and connect your repo.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Set environment variables (if needed) and deploy.

Notes:
- Keep `generated_files/` out of the repo; it's ignored by `.gitignore`.
- If you need database or secrets, add them in Render's environment settings.
