# HOYBOOKING

Hotel Booking Management System (Flask + MySQL + HTML/CSS/JS).

## Setup
1. Create a MySQL database named `hoybooking` (or set `HOYBOOKING_DB_NAME`).
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Set environment variables (recommended) or use defaults in `config.py`:
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

