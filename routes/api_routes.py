from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from flask import Blueprint, jsonify, request, session
from sqlalchemy import or_

from models.booking import Booking
from models.extensions import db
from models.payment import Payment
from models.room import Room
from models.user import User

api_bp = Blueprint("api", __name__, url_prefix="/api")


def parse_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def require_login():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401
    return None


@api_bp.get("/rooms")
def api_rooms():
    check_in_str = request.args.get("check_in")
    check_out_str = request.args.get("check_out")
    room_type = request.args.get("room_type")
    q = (request.args.get("q") or "").strip()
    price_min_raw = request.args.get("price_min")
    price_max_raw = request.args.get("price_max")

    check_in = parse_date(check_in_str)
    check_out = parse_date(check_out_str)

    rooms_q = Room.query
    if room_type:
        rooms_q = rooms_q.filter(Room.room_type == room_type)
    if q:
        rooms_q = rooms_q.filter(
            or_(
                Room.room_number.ilike(f"%{q}%"),
                Room.room_type.ilike(f"%{q}%"),
            )
        )

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

    if price_min is not None:
        rooms_q = rooms_q.filter(Room.price >= price_min)
    if price_max is not None:
        rooms_q = rooms_q.filter(Room.price <= price_max)

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
        rooms = rooms_q.filter(Room.status == "available").filter(~Room.id.in_(conflicting_room_ids)).all()
    else:
        rooms = rooms_q.filter(Room.status == "available").order_by(Room.room_number.asc()).all()

    return jsonify(
        {
            "ok": True,
            "rooms": [
                {
                    "id": r.id,
                    "room_number": r.room_number,
                    "room_type": r.room_type,
                    "price": float(r.price),
                    "status": r.status,
                    "image": r.image,
                    "images": [img.image_path for img in r.images],
                    "image_count": len(r.images),
                    "unit_rooms": r.unit_rooms,
                    "capacity": r.capacity,
                }
                for r in rooms
            ],
        }
    )


@api_bp.get("/me")
def api_me():
    auth_err = require_login()
    if auth_err:
        return auth_err
    user = User.query.get(session.get("user_id"))
    if not user:
        return jsonify({"ok": False, "error": "User not found"}), 404
    return jsonify({"ok": True, "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}})


@api_bp.get("/bookings")
def api_bookings():
    auth_err = require_login()
    if auth_err:
        return auth_err
    bookings = (
        Booking.query.filter_by(user_id=session.get("user_id"))
        .order_by(Booking.created_at.desc())
        .all()
    )
    out = []
    for b in bookings:
        payment = Payment.query.filter_by(booking_id=b.id).first()
        out.append(
            {
                "id": b.id,
                "room_id": b.room_id,
                "check_in_date": b.check_in_date.isoformat(),
                "check_out_date": b.check_out_date.isoformat(),
                "total_price": float(b.total_price),
                "status": b.status,
                "payment": {
                    "payment_status": payment.payment_status if payment else None,
                    "payment_method": payment.payment_method if payment else None,
                },
            }
        )
    return jsonify({"ok": True, "bookings": out})


@api_bp.post("/bookings/create")
def api_create_booking():
    auth_err = require_login()
    if auth_err:
        return auth_err
    if session.get("role") != "customer":
        return jsonify({"ok": False, "error": "Customer only"}), 403

    payload = request.get_json(silent=True) or {}
    room_id = payload.get("room_id")
    check_in = parse_date(payload.get("check_in_date"))
    check_out = parse_date(payload.get("check_out_date"))
    guest_count = int(payload.get("guest_count") or 1)

    if not room_id or not check_in or not check_out or check_out <= check_in or guest_count <= 0:
        return jsonify({"ok": False, "error": "Invalid input"}), 400

    room = Room.query.get(int(room_id))
    if not room:
        return jsonify({"ok": False, "error": "Room not found"}), 404

    if room.status != "available":
        return jsonify({"ok": False, "error": "This room is not available now"}), 409
    if room.capacity and guest_count > room.capacity:
        return jsonify({"ok": False, "error": f"This room supports up to {room.capacity} guests"}), 400

    conflict = (
        Booking.query.filter(
            Booking.room_id == room.id,
            Booking.status != "cancelled",
            Booking.check_in_date < check_out,
            Booking.check_out_date > check_in,
        ).first()
    )
    if conflict:
        return jsonify({"ok": False, "error": "This room is not available now"}), 409

    nights = (check_out - check_in).days
    total_price = (Decimal(room.price) * Decimal(nights)).quantize(Decimal("0.01"))

    booking = Booking(
        user_id=session.get("user_id"),
        room_id=room.id,
        check_in_date=check_in,
        check_out_date=check_out,
        total_price=total_price,
        guest_count=guest_count,
        status="confirmed",
    )
    db.session.add(booking)
    db.session.flush()

    # Mark room unavailable immediately after successful booking.
    room.status = "booked"
    payment = Payment(
        booking_id=booking.id,
        amount=total_price,
        payment_method=None,
        payment_status="unpaid",
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({"ok": True, "booking_id": booking.id})


@api_bp.post("/payments/pay")
def api_pay():
    auth_err = require_login()
    if auth_err:
        return auth_err
    if session.get("role") != "customer":
        return jsonify({"ok": False, "error": "Customer only"}), 403

    payload = request.get_json(silent=True) or {}
    booking_id = payload.get("booking_id")
    method = (payload.get("payment_method") or "").strip().lower()

    if not booking_id or method not in ["evc_plus", "edahab", "salaam_bank"]:
        return jsonify({"ok": False, "error": "Invalid input"}), 400

    booking = Booking.query.get(int(booking_id))
    if not booking or booking.user_id != session.get("user_id"):
        return jsonify({"ok": False, "error": "Booking not found"}), 404

    payment = Payment.query.filter_by(booking_id=booking.id).first()
    if not payment:
        payment = Payment(booking_id=booking.id, amount=booking.total_price, payment_method=method, payment_status="paid")
        db.session.add(payment)
    else:
        payment.payment_method = method
        payment.payment_status = "paid"

    db.session.commit()
    return jsonify({"ok": True, "payment_status": payment.payment_status})

