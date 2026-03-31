from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from flask import Blueprint, abort, flash, render_template, request, send_from_directory
from sqlalchemy import or_

from models.booking import Booking
from models.contact_message import ContactMessage
from models.extensions import db
from models.room import Room

public_bp = Blueprint("public", __name__)
CREATIVO_ASSETS_DIR = Path(__file__).resolve().parent.parent / "templates" / "Creativo" / "assets"


def parse_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@public_bp.route("/creativo-assets/<path:filename>")
def creativo_assets(filename: str):
    # Serve bundled Creativo assets directly from the template package.
    full_path = CREATIVO_ASSETS_DIR / filename
    if not full_path.exists() or not full_path.is_file():
        abort(404)
    return send_from_directory(CREATIVO_ASSETS_DIR, filename)


@public_bp.route("/")
def home():
    check_in_str = request.args.get("check_in")
    check_out_str = request.args.get("check_out")
    room_type = request.args.get("room_type")  # optional
    q = (request.args.get("q") or "").strip()
    room_types = ["single", "double", "deluxe", "apartment"]

    check_in = parse_date(check_in_str)
    check_out = parse_date(check_out_str)

    price_min_raw = request.args.get("price_min")
    price_max_raw = request.args.get("price_max")
    price_min = None
    price_max = None
    try:
        if price_min_raw not in (None, ""):
            price_min = Decimal(price_min_raw)
    except Exception:
        price_min = None
    try:
        if price_max_raw not in (None, ""):
            price_max = Decimal(price_max_raw)
    except Exception:
        price_max = None

    rooms_q = Room.query
    if room_type and room_type in room_types:
        rooms_q = rooms_q.filter(Room.room_type == room_type)
    if q:
        rooms_q = rooms_q.filter(
            or_(
                Room.room_number.ilike(f"%{q}%"),
                Room.room_type.ilike(f"%{q}%"),
            )
        )
    if price_min is not None:
        rooms_q = rooms_q.filter(Room.price >= price_min)
    if price_max is not None:
        rooms_q = rooms_q.filter(Room.price <= price_max)

    available_rooms = []
    message = None
    selected_room_type = room_type or ""

    if check_in and check_out:
        if check_out <= check_in:
            message = "Check-out date must be after check-in."
        else:
            conflicting_room_ids = (
                db.session.query(Booking.room_id)
                .filter(
                    Booking.status != "cancelled",
                    Booking.check_in_date < check_out,
                    Booking.check_out_date > check_in,
                )
                .subquery()
            )
            available_rooms = (
                rooms_q.filter(Room.status == "available")
                .filter(~Room.id.in_(conflicting_room_ids))
                .order_by(Room.room_number.asc())
                .all()
            )
    else:
        available_rooms = rooms_q.filter(Room.status == "available").order_by(Room.room_number.asc()).all()

    # Dynamic apartment preview section (independent block on homepage).
    apartment_q = Room.query.filter(Room.status == "available", Room.room_type == "apartment")
    if check_in and check_out and check_out > check_in:
        conflicting_room_ids = (
            db.session.query(Booking.room_id)
            .filter(
                Booking.status != "cancelled",
                Booking.check_in_date < check_out,
                Booking.check_out_date > check_in,
            )
            .subquery()
        )
        apartment_q = apartment_q.filter(~Room.id.in_(conflicting_room_ids))
    apartment_rooms = apartment_q.order_by(Room.id.desc()).limit(3).all()
    total_rooms_count = Room.query.count()
    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status="confirmed").count()
    happy_rate = int((confirmed_bookings / total_bookings) * 100) if total_bookings > 0 else 98

    return render_template(
        "index.html",
        rooms=available_rooms,
        apartment_rooms=apartment_rooms,
        total_rooms_count=total_rooms_count,
        happy_rate=happy_rate,
        room_types=room_types,
        check_in=check_in_str or "",
        check_out=check_out_str or "",
        selected_room_type=selected_room_type,
        price_min=price_min_raw or "",
        price_max=price_max_raw or "",
        q=q,
        message=message,
    )


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        phone = (request.form.get("phone") or "").strip()
        subject = (request.form.get("subject") or "").strip()
        message = (request.form.get("message") or "").strip()

        if not name or not email or not subject or not message:
            flash("Please fill in name, email, subject, and message.", "warning")
            return render_template("contact.html")

        msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )
        db.session.add(msg)
        db.session.commit()
        flash("Your message has been sent successfully.", "success")

    return render_template("contact.html")


@public_bp.route("/rooms")
def rooms():
    check_in_str = request.args.get("check_in")
    check_out_str = request.args.get("check_out")
    room_type = request.args.get("room_type")  # optional
    q = (request.args.get("q") or "").strip()
    room_types = ["single", "double", "deluxe", "apartment"]

    check_in = parse_date(check_in_str)
    check_out = parse_date(check_out_str)

    rooms_q = Room.query
    if room_type and room_type in room_types:
        rooms_q = rooms_q.filter(Room.room_type == room_type)
    if q:
        rooms_q = rooms_q.filter(
            or_(
                Room.room_number.ilike(f"%{q}%"),
                Room.room_type.ilike(f"%{q}%"),
            )
        )

    price_min_raw = request.args.get("price_min")
    price_max_raw = request.args.get("price_max")
    try:
        if price_min_raw not in (None, ""):
            rooms_q = rooms_q.filter(Room.price >= Decimal(price_min_raw))
    except Exception:
        pass
    try:
        if price_max_raw not in (None, ""):
            rooms_q = rooms_q.filter(Room.price <= Decimal(price_max_raw))
    except Exception:
        pass

    rooms_list = []
    room_availability = {}
    message = None
    if check_in and check_out:
        if check_out <= check_in:
            message = "Check-out date must be after check-in."
        else:
            # A room is conflicting if an existing booking overlaps the requested range.
            # Overlap condition:
            #   new_check_in < existing_check_out AND new_check_out > existing_check_in
            conflicting_room_ids_q = (
                db.session.query(Booking.room_id)
                .filter(
                    Booking.status != "cancelled",
                    Booking.check_in_date < check_out,
                    Booking.check_out_date > check_in,
                )
                .distinct()
            )
            conflicting_ids = {row[0] for row in conflicting_room_ids_q.all()}

            rooms_list = rooms_q.order_by(Room.room_number.asc()).all()
            for r in rooms_list:
                is_available = (r.status == "available") and (r.id not in conflicting_ids)
                room_availability[r.id] = is_available
    else:
        # If no dates provided, show all rooms but availability depends only on `rooms.status`.
        rooms_list = rooms_q.order_by(Room.room_number.asc()).all()
        for r in rooms_list:
            room_availability[r.id] = r.status == "available"

    return render_template(
        "rooms.html",
        rooms=rooms_list,
        room_types=room_types,
        check_in=check_in_str or "",
        check_out=check_out_str or "",
        selected_room_type=room_type or "",
        message=message,
        price_min=price_min_raw or "",
        price_max=price_max_raw or "",
        q=q,
        room_availability=room_availability,
    )


@public_bp.route("/rooms/<int:room_id>")
def room_details(room_id: int):
    room = Room.query.get(room_id)
    if not room:
        abort(404)

    check_in_str = request.args.get("check_in") or ""
    check_out_str = request.args.get("check_out") or ""
    check_in = parse_date(check_in_str)
    check_out = parse_date(check_out_str)

    is_available = room.status == "available"
    if check_in and check_out and check_out > check_in:
        conflict = (
            Booking.query.filter(
                Booking.room_id == room.id,
                Booking.status != "cancelled",
                Booking.check_in_date < check_out,
                Booking.check_out_date > check_in,
            ).first()
        )
        if conflict:
            is_available = False

    gallery_images = [img.image_path for img in room.images]
    if not gallery_images and room.image:
        gallery_images = [room.image]
    if not gallery_images:
        gallery_images = ["__fallback__"]

    return render_template(
        "room_details.html",
        room=room,
        check_in=check_in_str,
        check_out=check_out_str,
        is_available=is_available,
        gallery_images=gallery_images,
    )

