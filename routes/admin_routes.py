from __future__ import annotations

import os
import re
import uuid
from decimal import Decimal

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy import func
from werkzeug.utils import secure_filename

from models.booking import Booking
from models.contact_message import ContactMessage
from models.extensions import bcrypt
from models.extensions import db
from models.payment import Payment
from models.room import Room
from models.room_image import RoomImage
from models.user import User

from utils.auth import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def save_room_image(file_storage, upload_dir: str):
    if not file_storage or not file_storage.filename:
        return None

    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        return None

    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(f"{uuid.uuid4().hex}{ext}")
    target_path = os.path.join(upload_dir, filename)
    file_storage.save(target_path)
    # Store relative path under static/
    return f"images/{filename}"


def save_room_images(files, upload_dir: str):
    image_paths = []
    for f in files or []:
        path = save_room_image(f, upload_dir)
        if path:
            image_paths.append(path)
        elif f and f.filename:
            return None  # invalid type in selection
    return image_paths


@admin_bp.route("/")
@admin_required
def admin_dashboard():
    users_count = User.query.count()
    rooms_count = Room.query.count()
    bookings_count = Booking.query.count()
    payments_count = Payment.query.count()

    confirmed_count = Booking.query.filter_by(status="confirmed").count()
    cancelled_count = Booking.query.filter_by(status="cancelled").count()
    revenue_paid = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.payment_status == "paid").scalar()
    )
    return render_template(
        "admin_dashboard.html",
        users_count=users_count,
        rooms_count=rooms_count,
        bookings_count=bookings_count,
        payments_count=payments_count,
        confirmed_count=confirmed_count,
        cancelled_count=cancelled_count,
        revenue_paid=revenue_paid,
    )


@admin_bp.route("/rooms")
@admin_required
def admin_rooms():
    rooms = Room.query.order_by(Room.room_number.asc()).all()
    return render_template("admin_rooms.html", rooms=rooms)


@admin_bp.route("/rooms/new", methods=["GET", "POST"])
@admin_required
def admin_room_new():
    if request.method == "POST":
        room_number = (request.form.get("room_number") or "").strip()
        room_type = (request.form.get("room_type") or "").strip().lower()
        price_raw = (request.form.get("price") or "").strip()
        status = (request.form.get("status") or "available").strip().lower()
        unit_rooms_raw = (request.form.get("unit_rooms") or "1").strip()
        capacity_raw = (request.form.get("capacity") or "2").strip()

        try:
            price = Decimal(price_raw)
        except Exception:
            flash("Invalid price.", "warning")
            return redirect(url_for("admin.admin_room_new"))
        try:
            unit_rooms = int(unit_rooms_raw)
            capacity = int(capacity_raw)
        except Exception:
            flash("Invalid apartment details (rooms/capacity).", "warning")
            return redirect(url_for("admin.admin_room_new"))

        if not room_number or not room_type or price <= 0 or unit_rooms <= 0 or capacity <= 0:
            flash("Room number, type, and valid price are required.", "warning")
            return redirect(url_for("admin.admin_room_new"))

        upload_dir = current_app.config["ROOM_IMAGE_UPLOAD_DIR"]
        image_path = save_room_image(request.files.get("image"), upload_dir)
        if request.files.get("image") and not image_path:
            flash("Invalid cover image type. Allowed: jpg, jpeg, png, webp, gif.", "warning")
            return redirect(url_for("admin.admin_room_new"))
        gallery_paths = save_room_images(request.files.getlist("images"), upload_dir)
        if gallery_paths is None:
            flash("Invalid gallery image type. Allowed: jpg, jpeg, png, webp, gif.", "warning")
            return redirect(url_for("admin.admin_room_new"))
        if len(gallery_paths) < 4:
            flash("Please upload at least 4 room images.", "warning")
            return redirect(url_for("admin.admin_room_new"))

        room = Room(
            room_number=room_number,
            room_type=room_type,
            price=price,
            status=status or "available",
            image=image_path,
            unit_rooms=unit_rooms,
            capacity=capacity,
        )
        db.session.add(room)
        try:
            db.session.flush()
            for idx, p in enumerate(gallery_paths):
                db.session.add(RoomImage(room_id=room.id, image_path=p, sort_order=idx))
            if not room.image and gallery_paths:
                room.image = gallery_paths[0]
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Room number already exists or invalid data.", "danger")
            return redirect(url_for("admin.admin_room_new"))

        flash("Room added.", "success")
        return redirect(url_for("admin.admin_rooms"))

    return render_template("admin_room_form.html", room=None)


@admin_bp.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_room_edit(room_id: int):
    room = Room.query.get(room_id)
    if not room:
        flash("Room not found.", "danger")
        return redirect(url_for("admin.admin_rooms"))

    if request.method == "POST":
        room_number = (request.form.get("room_number") or "").strip()
        room_type = (request.form.get("room_type") or "").strip().lower()
        price_raw = (request.form.get("price") or "").strip()
        status = (request.form.get("status") or "available").strip().lower()
        unit_rooms_raw = (request.form.get("unit_rooms") or "1").strip()
        capacity_raw = (request.form.get("capacity") or "2").strip()

        try:
            price = Decimal(price_raw)
        except Exception:
            flash("Invalid price.", "warning")
            return redirect(url_for("admin.admin_room_edit", room_id=room_id))
        try:
            unit_rooms = int(unit_rooms_raw)
            capacity = int(capacity_raw)
        except Exception:
            flash("Invalid apartment details (rooms/capacity).", "warning")
            return redirect(url_for("admin.admin_room_edit", room_id=room_id))

        if not room_number or not room_type or price <= 0 or unit_rooms <= 0 or capacity <= 0:
            flash("Room number, type, and valid price are required.", "warning")
            return redirect(url_for("admin.admin_room_edit", room_id=room_id))

        upload_dir = current_app.config["ROOM_IMAGE_UPLOAD_DIR"]
        image_path = save_room_image(request.files.get("image"), upload_dir)
        if request.files.get("image") and not image_path:
            flash("Invalid cover image type. Allowed: jpg, jpeg, png, webp, gif.", "warning")
            return redirect(url_for("admin.admin_room_edit", room_id=room_id))
        gallery_paths = save_room_images(request.files.getlist("images"), upload_dir)
        if gallery_paths is None:
            flash("Invalid gallery image type. Allowed: jpg, jpeg, png, webp, gif.", "warning")
            return redirect(url_for("admin.admin_room_edit", room_id=room_id))

        room.room_number = room_number
        room.room_type = room_type
        room.price = price
        room.status = status or "available"
        room.unit_rooms = unit_rooms
        room.capacity = capacity
        if image_path:
            room.image = image_path
        if gallery_paths:
            max_sort = db.session.query(func.coalesce(func.max(RoomImage.sort_order), -1)).filter(RoomImage.room_id == room.id).scalar()
            for idx, p in enumerate(gallery_paths):
                db.session.add(RoomImage(room_id=room.id, image_path=p, sort_order=max_sort + 1 + idx))
        # Enforce minimum 4 images per room.
        current_count = RoomImage.query.filter_by(room_id=room.id).count() + (len(gallery_paths) if gallery_paths else 0)
        if current_count < 4:
            flash("Each room must have at least 4 images.", "warning")
            return redirect(url_for("admin.admin_room_edit", room_id=room_id))
        db.session.commit()
        flash("Room updated.", "success")
        return redirect(url_for("admin.admin_rooms"))

    return render_template("admin_room_form.html", room=room)


@admin_bp.route("/rooms/<int:room_id>/images/<int:image_id>/delete", methods=["POST"])
@admin_required
def admin_room_image_delete(room_id: int, image_id: int):
    room = Room.query.get(room_id)
    image = RoomImage.query.get(image_id)
    if not room or not image or image.room_id != room.id:
        flash("Image not found.", "danger")
        return redirect(url_for("admin.admin_room_edit", room_id=room_id))

    count = RoomImage.query.filter_by(room_id=room.id).count()
    if count <= 4:
        flash("A room must keep at least 4 images.", "warning")
        return redirect(url_for("admin.admin_room_edit", room_id=room_id))

    if room.image == image.image_path:
        replacement = RoomImage.query.filter(RoomImage.room_id == room.id, RoomImage.id != image.id).first()
        room.image = replacement.image_path if replacement else None

    db.session.delete(image)
    db.session.commit()
    flash("Image removed.", "success")
    return redirect(url_for("admin.admin_room_edit", room_id=room_id))


@admin_bp.route("/rooms/<int:room_id>/delete", methods=["POST"])
@admin_required
def admin_room_delete(room_id: int):
    room = Room.query.get(room_id)
    if not room:
        flash("Room not found.", "danger")
        return redirect(url_for("admin.admin_rooms"))

    db.session.delete(room)
    db.session.commit()
    flash("Room deleted.", "success")
    return redirect(url_for("admin.admin_rooms"))


@admin_bp.route("/bookings")
@admin_required
def admin_bookings():
    status = (request.args.get("status") or "").strip().lower()
    q = Booking.query
    if status in ["confirmed", "cancelled"]:
        q = q.filter(Booking.status == status)
    bookings = q.order_by(Booking.created_at.desc()).all()
    return render_template("admin_bookings.html", bookings=bookings)


@admin_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
@admin_required
def admin_booking_update_status(booking_id: int):
    booking = Booking.query.get(booking_id)
    if not booking:
        flash("Booking not found.", "danger")
        return redirect(url_for("admin.admin_bookings"))

    new_status = (request.form.get("status") or "").strip().lower()
    if new_status not in ["confirmed", "cancelled"]:
        flash("Invalid status.", "warning")
        return redirect(url_for("admin.admin_bookings"))

    booking.status = new_status

    # Keep rooms.status in sync based on whether any confirmed bookings exist.
    room = Room.query.get(booking.room_id)
    if room:
        any_confirmed = Booking.query.filter_by(room_id=room.id).filter(Booking.status == "confirmed").count() > 0
        room.status = "booked" if any_confirmed else "available"

    db.session.commit()
    flash("Booking status updated.", "success")
    return redirect(url_for("admin.admin_bookings"))


@admin_bp.route("/users")
@admin_required
def admin_users():
    users = User.query.order_by(User.id.desc()).all()
    return render_template("admin_users.html", users=users)


@admin_bp.route("/users/admins/new", methods=["POST"])
@admin_required
def admin_create_admin_user():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    if not name or not email or not password:
        flash("Name, email, and password are required.", "warning")
        return redirect(url_for("admin.admin_users"))
    if len(password) < 8:
        flash("Admin password must be at least 8 characters.", "warning")
        return redirect(url_for("admin.admin_users"))
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        flash("Admin password must include letters and numbers.", "warning")
        return redirect(url_for("admin.admin_users"))
    if User.query.filter_by(email=email).first():
        flash("Email already exists. Use a unique admin email.", "warning")
        return redirect(url_for("admin.admin_users"))

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    admin_user = User(name=name, email=email, password=hashed, role="admin")
    db.session.add(admin_user)
    db.session.commit()
    flash("Admin account created successfully.", "success")
    return redirect(url_for("admin.admin_users"))


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def admin_user_update_role(user_id: int):
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.admin_users"))

    new_role = (request.form.get("role") or "").strip().lower()
    if new_role not in ["admin", "customer"]:
        flash("Invalid role.", "warning")
        return redirect(url_for("admin.admin_users"))

    user.role = new_role
    db.session.commit()
    flash("User role updated.", "success")
    return redirect(url_for("admin.admin_users"))


@admin_bp.route("/payments")
@admin_required
def admin_payments():
    payments = (
        Payment.query.order_by(Payment.id.desc())
        .all()
    )
    return render_template("admin_payments.html", payments=payments)


@admin_bp.route("/contact-messages")
@admin_required
def admin_contact_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin_contact_messages.html", messages=messages)

