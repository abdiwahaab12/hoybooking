from __future__ import annotations

from datetime import date

from .extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)

    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    guest_count = db.Column(db.Integer, nullable=False, default=1)

    status = db.Column(db.String(20), nullable=False, default="confirmed")  # confirmed/cancelled

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user = db.relationship("User", back_populates="bookings")
    room = db.relationship("Room", back_populates="bookings")
    payments = db.relationship("Payment", back_populates="booking", cascade="all, delete-orphan")

    def nights(self) -> int:
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0

    def __repr__(self) -> str:
        return f"<Booking {self.id} user={self.user_id} room={self.room_id}>"

