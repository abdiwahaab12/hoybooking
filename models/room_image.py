from __future__ import annotations

from .extensions import db


class RoomImage(db.Model):
    __tablename__ = "room_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False, index=True)
    image_path = db.Column(db.String(255), nullable=False)
    label = db.Column(db.String(50), nullable=True)  # e.g., living room, bedroom, kitchen, bathroom
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    room = db.relationship("Room", back_populates="images")

    def __repr__(self) -> str:
        return f"<RoomImage room={self.room_id} id={self.id}>"

