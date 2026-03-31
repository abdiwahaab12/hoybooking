from __future__ import annotations

from .extensions import db


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_number = db.Column(db.String(20), nullable=False, unique=True, index=True)
    # Keep the DB column name as `type` per requirements, but use attribute `room_type` (type is reserved in Python).
    room_type = db.Column("type", db.String(20), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="available")
    image = db.Column(db.String(255), nullable=True)
    # For apartment/family rooms.
    unit_rooms = db.Column(db.Integer, nullable=False, default=1)
    capacity = db.Column(db.Integer, nullable=False, default=2)

    bookings = db.relationship("Booking", back_populates="room", cascade="all, delete-orphan")
    images = db.relationship("RoomImage", back_populates="room", cascade="all, delete-orphan", order_by="RoomImage.sort_order")

    def __repr__(self) -> str:
        return f"<Room {self.room_number} ({self.room_type})>"

