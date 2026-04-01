# HOYBOOKING

Hotel Booking Management System (Flask + MySQL + HTML/CSS/JS).

## Setup
1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run with SQLite (default, local/no DB setup needed):
   - `python app.py`
3. Optional: run with MySQL instead by setting `HOYBOOKING_DB_BACKEND=mysql` (or `HOYBOOKING_USE_MYSQL=true`) and these variables:
   - `HOYBOOKING_DB_HOST` (default `127.0.0.1`)
   - `HOYBOOKING_DB_PORT` (default `3306`)
   - `HOYBOOKING_DB_USER` (default `root`)
   - `HOYBOOKING_DB_PASSWORD`
   - `HOYBOOKING_DB_NAME` (default `hoybooking`)
   - `HOYBOOKING_SECRET_KEY`

## Run
- `python app.py`

## Schema updates included
- `rooms.status` (`available` / `booked`)
- `rooms.image` (path under `static/images/`)
- `rooms.unit_rooms` (for apartment/family setup)
- `rooms.capacity` (max guests)
- `bookings.guest_count`

These columns are auto-added on startup if missing.

## Admin account
- Register creates `customer` users.
- Use the Admin → Manage Users page to promote a user to `admin` (after you login).
- For deployment, set these env vars so admin is always available after deploy:
  - `HOYBOOKING_ADMIN_EMAIL`
  - `HOYBOOKING_ADMIN_PASSWORD`
  - `HOYBOOKING_ADMIN_NAME` (optional, default `Admin`)
  - `HOYBOOKING_ADMIN_RESET_ON_START` (`true` to reset password every restart; default `false`)

## Render deploy (recommended)
- Create a **Web Service** from your GitHub repo.
- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Set env vars in Render:
  - `HOYBOOKING_SECRET_KEY` = a long random value
  - `HOYBOOKING_DB_BACKEND` = `mysql` (if using Render MySQL)
  - `HOYBOOKING_DATABASE_URL` = your Render MySQL internal URL (preferred)
  - `HOYBOOKING_ADMIN_EMAIL` = your admin email
  - `HOYBOOKING_ADMIN_PASSWORD` = strong password
  - `HOYBOOKING_ADMIN_RESET_ON_START` = `false`
- After deploy, open `/db-test` once to confirm DB connectivity returns `{"ok": true}`.

