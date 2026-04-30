# VibeTune AI Song Finder 🎵

Mood-led music recommendations powered by a Python Flask backend with user authentication.

## Project Structure

```
vibetune/
├── app.py                  # Flask backend (auth, profile, favorites API)
├── requirements.txt
├── users_db.json           # Auto-created on first signup (file-based DB)
├── templates/
│   ├── auth.html           # Login & Signup page
│   └── index.html          # Main app
└── static/
    ├── css/styles.css      # Dark musical theme
    └── js/script.js        # Frontend logic (Flask-backed)
```

## Setup & Run

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

Optional:
```bash
FLASK_DEBUG=1 PORT=5000 python app.py
```

By default, user data is stored in `users_db.json` next to the app when that folder is writable. If not, VibeTune falls back to `~/.vibetune/users_db.json`, and finally to a temp directory in restricted environments. You can also override this with `VIBETUNE_USERS_FILE` or `VIBETUNE_DATA_DIR`.

## What's New

### ✅ Python Backend (Flask)
- Full REST API: `/api/signup`, `/api/login`, `/api/logout`
- Profile management: `GET/POST /api/profile`
- Favorites: `POST /api/favorites`, `DELETE /api/favorites/<idx>`
- Session-based authentication (server-side)
- File-based JSON "database" (`users_db.json`) — easy to swap for SQLite/Postgres

### ✅ Login & Sign Up
- Beautiful dark auth page with animated musical background
- Email + password authentication
- Passwords hashed with Werkzeug (bcrypt-style)
- Protected routes — unauthenticated users redirected to `/login`

### ✅ Musical Design
- Floating animated music notes (♪ ♫ ♩ ♬)
- Animated equalizer bar in the sidebar
- Waveform animation in the hero card
- Rotating vinyl record decoration
- Staff lines background
- Dark purple/violet theme with mood-reactive accent colors
- Playfair Display serif font for headings

## Production Notes

- Change `SECRET_KEY` via environment variable: `export SECRET_KEY=your-secret`
- Swap `users_db.json` for a proper database (SQLite, PostgreSQL, etc.)
- Run behind a WSGI server (gunicorn, uWSGI) in production

## Deploy (Gunicorn)

This repo is now deploy-ready for platforms like Render/Railway/Heroku.

- Start command: `gunicorn app:app`
- Included `Procfile`: `web: gunicorn app:app`
- Health check endpoint: `GET /health`

Environment variables to set in production:

- `SECRET_KEY` (required, strong random string)
- `PORT` (usually injected by platform)
- `SESSION_COOKIE_SECURE=1` (recommended on HTTPS)

Local production-like run:

```bash
pip install -r requirements.txt
SECRET_KEY=change-me gunicorn app:app --bind 0.0.0.0:${PORT:-5000}
```
