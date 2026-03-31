from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.booking import Booking
from models.extensions import db
from models.payment import Payment
from models.room import Room

from utils.auth import login_required

booking_bp = Blueprint("booking", __name__)


def parse_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def nights_between(check_in, check_out) -> int:
    return (check_out - check_in).days


def get_room_types():
    return ["single", "double", "deluxe", "apartment"]


def get_booking_draft():
    draft = session.get("booking_draft")
    if not draft:
        return None
    try:
        room_id = int(draft["room_id"])
        guest_count = int(draft.get("guest_count", 1))
        check_in = parse_date(draft.get("check_in_date"))
        check_out = parse_date(draft.get("check_out_date"))
        if not check_in or not check_out or guest_count <= 0:
            return None
        return {"room_id": room_id, "check_in": check_in, "check_out": check_out, "guest_count": guest_count}
    except Exception:
        return None


@booking_bp.route("/dashboard")
@login_required
def customer_dashboard():
    if session.get("role") != "customer":
        flash("Customer dashboard is for customers only.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    check_in_str = request.args.get("check_in")
    check_out_str = request.args.get("check_out")
    room_type = request.args.get("room_type")

    check_in = parse_date(check_in_str)
    check_out = parse_date(check_out_str)
    room_types = get_room_types()

    available_rooms = []
    message = None

    rooms_q = Room.query.filter(Room.status == "available")
    if room_type in room_types:
        rooms_q = rooms_q.filter(Room.room_type == room_type)

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
            available_rooms = rooms_q.filter(~Room.id.in_(conflicting_room_ids)).order_by(Room.room_number).all()
    else:
        # If no dates provided, show all rooms.
        available_rooms = rooms_q.order_by(Room.room_number.asc()).all()

    my_bookings = (
        Booking.query.filter_by(user_id=session.get("user_id"))
        .order_by(Booking.created_at.desc())
        .all()
    )

    return render_template(
        "dashboard.html",
        rooms=available_rooms,
        room_types=room_types,
        check_in=check_in_str or "",
        check_out=check_out_str or "",
        selected_room_type=room_type or "",
        message=message,
        bookings=my_bookings,
    )


@booking_bp.route("/booking/start", methods=["POST"])
def start_booking():
    """
    Booking step 1 (guest-friendly):
    Store selection in session and redirect to confirmation.
    """
    room_id_raw = request.form.get("room_id")
    check_in_str = request.form.get("check_in_date")
    check_out_str = request.form.get("check_out_date")
    guest_count_raw = (request.form.get("guest_count") or "1").strip()

    check_in = parse_date(check_in_str)
    check_out = parse_date(check_out_str)

    if not room_id_raw or not check_in or not check_out or check_out <= check_in:
        flash("Invalid booking selection. Please choose valid dates.", "warning")
        return redirect(url_for("public.rooms"))

    try:
        room_id = int(room_id_raw)
        guest_count = int(guest_count_raw)
    except Exception:
        flash("Invalid room or guest value.", "warning")
        return redirect(url_for("public.rooms"))

    room = Room.query.get(room_id)
    if not room:
        flash("Room not found.", "danger")
        return redirect(url_for("public.rooms"))
    if guest_count <= 0:
        flash("Guest count must be at least 1.", "warning")
        return redirect(url_for("public.rooms"))
    if room.capacity and guest_count > room.capacity:
        flash(f"This room supports up to {room.capacity} guests.", "warning")
        return redirect(url_for("public.rooms"))

    session["booking_draft"] = {
        "room_id": room_id,
        "check_in_date": check_in_str,
        "check_out_date": check_out_str,
        "guest_count": guest_count,
    }
    return redirect(url_for("booking.confirm_booking"))


@booking_bp.route("/booking/confirm", methods=["GET", "POST"])
def confirm_booking():
    """
    Booking step 2:
    If not logged in, redirect to login/registration (next=confirm).
    If logged in, create booking + unpaid payment and redirect to payment stage.
    """
    draft = get_booking_draft()
    if not draft:
        flash("Please select a room first.", "warning")
        return redirect(url_for("public.home"))

    room = Room.query.get(draft["room_id"])
    if not room:
        flash("Room not found.", "danger")
        return redirect(url_for("public.rooms"))

    nights = nights_between(draft["check_in"], draft["check_out"])
    total_price = (Decimal(room.price) * Decimal(nights)).quantize(Decimal("0.01"))

    if request.method == "POST":
        if session.get("user_id") is None or session.get("role") != "customer":
            # Redirect customers to login; after login we come back to confirm.
            return redirect(url_for("auth.login", next=request.path))

        if room.status != "available":
            flash("This room is not available now", "danger")
            return redirect(
                url_for("public.rooms", check_in=draft["check_in"].isoformat(), check_out=draft["check_out"].isoformat())
            )

        # Prevent double booking using date-overlap logic.
        conflict = (
            Booking.query.filter(
                Booking.room_id == room.id,
                Booking.status != "cancelled",
                Booking.check_in_date < draft["check_out"],
                Booking.check_out_date > draft["check_in"],
            ).first()
        )
        if conflict:
            flash("This room is not available now", "danger")
            return redirect(
                url_for("public.rooms", check_in=draft["check_in"].isoformat(), check_out=draft["check_out"].isoformat())
            )

        booking = Booking(
            user_id=session.get("user_id"),
            room_id=room.id,
            check_in_date=draft["check_in"],
            check_out_date=draft["check_out"],
            total_price=total_price,
            guest_count=draft["guest_count"],
            status="confirmed",
        )
        db.session.add(booking)
        db.session.flush()  # booking.id

        # Mark the room as unavailable immediately after successful booking.
        room.status = "booked"

        payment = Payment(
            booking_id=booking.id,
            amount=total_price,
            payment_method=None,
            payment_status="unpaid",
        )
        db.session.add(payment)
        db.session.commit()

        session.pop("booking_draft", None)
        flash("Booking confirmed. Please complete payment.", "success")
        return redirect(url_for("booking.pay_booking", booking_id=booking.id))

    return render_template(
        "booking_confirm.html",
        room=room,
        check_in=draft["check_in"].isoformat(),
        check_out=draft["check_out"].isoformat(),
        guest_count=draft["guest_count"],
        nights=nights,
        total_price=total_price,
    )


@booking_bp.route("/bookings/create", methods=["POST"])
@login_required
def create_booking():
    if session.get("role") != "customer":
        flash("Only customers can create bookings.", "warning")
        return redirect(url_for("public.rooms"))

    from_date_str = request.form.get("check_in_date")
    to_date_str = request.form.get("check_out_date")
    room_id_raw = request.form.get("room_id")
    guest_count_raw = (request.form.get("guest_count") or "1").strip()

    try:
        room_id = int(room_id_raw)
        guest_count = int(guest_count_raw)
    except Exception:
        flash("Invalid booking input.", "warning")
        return redirect(url_for("booking.customer_dashboard"))
    check_in = parse_date(from_date_str)
    check_out = parse_date(to_date_str)

    if not check_in or not check_out:
        flash("Invalid dates.", "warning")
        return redirect(url_for("booking.customer_dashboard"))
    if check_out <= check_in:
        flash("Check-out must be after check-in.", "warning")
        return redirect(url_for("booking.customer_dashboard"))

    room = Room.query.get(room_id)
    if not room:
        flash("Room not found.", "danger")
        return redirect(url_for("public.rooms"))
    if guest_count <= 0:
        flash("Guest count must be at least 1.", "warning")
        return redirect(url_for("public.rooms"))
    if room.capacity and guest_count > room.capacity:
        flash(f"This room supports up to {room.capacity} guests.", "warning")
        return redirect(url_for("public.rooms"))

    if room.status != "available":
        flash("This room is not available now", "danger")
        return redirect(url_for("public.rooms", check_in=from_date_str, check_out=to_date_str))

    # Prevent double booking using date-overlap logic.
    # new_check_in < existing_check_out AND new_check_out > existing_check_in
    conflict = (
        Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status != "cancelled",
            Booking.check_in_date < check_out,
            Booking.check_out_date > check_in,
        )
        .first()
    )
    if conflict:
        flash("This room is not available now", "danger")
        return redirect(url_for("public.rooms", check_in=from_date_str, check_out=to_date_str))

    nights = nights_between(check_in, check_out)
    total_price = (Decimal(room.price) * Decimal(nights)).quantize(Decimal("0.01"))

    booking = Booking(
        user_id=session.get("user_id"),
        room_id=room_id,
        check_in_date=check_in,
        check_out_date=check_out,
        total_price=total_price,
        guest_count=guest_count,
        status="confirmed",
    )
    db.session.add(booking)
    db.session.flush()  # get booking.id before payment insert

    # Mark the room as unavailable immediately after successful booking.
    room.status = "booked"

    payment = Payment(
        booking_id=booking.id,
        amount=total_price,
        payment_method=None,
        payment_status="unpaid",
    )
    db.session.add(payment)
    db.session.commit()

    return redirect(url_for("booking.pay_booking", booking_id=booking.id))


@booking_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id: int):
    if session.get("role") != "customer":
        flash("Only customers can cancel bookings.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    booking = Booking.query.get(booking_id)
    if not booking or booking.user_id != session.get("user_id"):
        flash("Booking not found.", "danger")
        return redirect(url_for("booking.customer_dashboard"))

    if booking.status != "cancelled":
        booking.status = "cancelled"
        payment = Payment.query.filter_by(booking_id=booking.id).first()
        if payment and payment.payment_status != "paid":
            payment.payment_status = "cancelled"

        # If there are no other active bookings for this room, set it back to available.
        room = Room.query.get(booking.room_id)
        if room:
            any_active = (
                Booking.query.filter_by(room_id=room.id).filter(Booking.status != "cancelled").count() > 0
            )
            room.status = "booked" if any_active else "available"
        db.session.commit()
        flash("Booking cancelled.", "success")
    else:
        flash("Booking is already cancelled.", "warning")

    return redirect(url_for("booking.customer_dashboard"))


@booking_bp.route("/bookings/<int:booking_id>/pay", methods=["GET", "POST"])
@login_required
def pay_booking(booking_id: int):
    if session.get("role") != "customer":
        flash("Payments are for customers.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    booking = Booking.query.get(booking_id)
    if not booking or booking.user_id != session.get("user_id"):
        flash("Booking not found.", "danger")
        return redirect(url_for("booking.customer_dashboard"))

    payment = Payment.query.filter_by(booking_id=booking.id).first()
    if request.method == "POST":
        method = (request.form.get("payment_method") or "").strip().lower()
        if method not in ["evc_plus", "edahab", "salaam_bank"]:
            flash("Invalid payment method.", "warning")
            return redirect(url_for("booking.pay_booking", booking_id=booking.id))

        if not payment:
            payment = Payment(
                booking_id=booking.id,
                amount=booking.total_price,
                payment_method=method,
                payment_status="paid",
            )
            db.session.add(payment)
        else:
            payment.payment_method = method
            payment.payment_status = "paid"

        # Booking remains confirmed; cancellation is separate.
        db.session.commit()
        flash("Payment successful (simulated).", "success")
        return redirect(url_for("booking.customer_dashboard"))

    return render_template("pay_booking.html", booking=booking, payment=payment)

