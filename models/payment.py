from __future__ import annotations

from .extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False, unique=True)

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(30), nullable=True)  # cash or mobile
    payment_status = db.Column(db.String(20), nullable=False, default="unpaid")

    booking = db.relationship("Booking", back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment booking={self.booking_id} status={self.payment_status}>"

