from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, url_for
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect as sa_inspect, text

from config import Config
from models import bcrypt, db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["ROOM_IMAGE_UPLOAD_DIR"] = str(Path(app.root_path) / "static" / "images")

    db.init_app(app)
    bcrypt.init_app(app)

    # Blueprints
    from routes.auth_routes import auth_bp
    from routes.public_routes import public_bp
    from routes.booking_routes import booking_bp
    from routes.admin_routes import admin_bp
    from routes.api_routes import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_user():
        from utils.auth import get_current_user

        user = get_current_user()
        return {"current_user": user}

    # Create tables on startup (good for a first build; use migrations for production).
    # If MySQL isn't running yet, allow the server to start so you can verify config.
    with app.app_context():
        try:
            db.create_all()
        except Exception as exc:
            print(
                "[HOYBOOKING] Warning: db.create_all() failed. "
                "Fix MySQL connectivity/credentials and restart.\n"
                f"Details: {exc}\n"
                "Env vars to check: HOYBOOKING_DB_HOST, HOYBOOKING_DB_PORT, HOYBOOKING_DB_USER, HOYBOOKING_DB_PASSWORD, HOYBOOKING_DB_NAME"
            )

        # Ensure `rooms.status` exists (add column if you already have a DB without it).
        try:
            inspector = sa_inspect(db.engine)
            if "rooms" in inspector.get_table_names():
                cols = {c["name"] for c in inspector.get_columns("rooms")}
                if "status" not in cols:
                    db.session.execute(
                        text("ALTER TABLE rooms ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'available'")
                    )
                    db.session.commit()
                if "image" not in cols:
                    db.session.execute(text("ALTER TABLE rooms ADD COLUMN image VARCHAR(255) NULL"))
                    db.session.commit()
                if "unit_rooms" not in cols:
                    db.session.execute(text("ALTER TABLE rooms ADD COLUMN unit_rooms INT NOT NULL DEFAULT 1"))
                    db.session.commit()
                if "capacity" not in cols:
                    db.session.execute(text("ALTER TABLE rooms ADD COLUMN capacity INT NOT NULL DEFAULT 2"))
                    db.session.commit()
            if "room_images" not in inspector.get_table_names():
                db.session.execute(
                    text(
                        "CREATE TABLE room_images ("
                        "id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,"
                        "room_id INT NOT NULL,"
                        "image_path VARCHAR(255) NOT NULL,"
                        "label VARCHAR(50) NULL,"
                        "sort_order INT NOT NULL DEFAULT 0,"
                        "INDEX ix_room_images_room_id (room_id),"
                        "CONSTRAINT fk_room_images_room FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE"
                        ")"
                    )
                )
                db.session.commit()
            if "bookings" in inspector.get_table_names():
                booking_cols = {c["name"] for c in inspector.get_columns("bookings")}
                if "guest_count" not in booking_cols:
                    db.session.execute(text("ALTER TABLE bookings ADD COLUMN guest_count INT NOT NULL DEFAULT 1"))
                    db.session.commit()
        except Exception as exc:
            print(f"[HOYBOOKING] Warning: failed to ensure rooms.status column: {exc}")

    @app.errorhandler(404)
    def not_found(_err):
        return render_template("error_404.html"), 404

    @app.errorhandler(500)
    def internal_error(_err):
        flash("Server error. Please try again.", "danger")
        return redirect(url_for("public.home"))

    @app.errorhandler(OperationalError)
    def db_error(err: OperationalError):
        # Avoid exposing credentials; show only connectivity context.
        return (
            render_template("error_db.html", error=str(err)),
            500,
        )

    @app.get("/db-test")
    def db_test():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"ok": True})
        except Exception as exc:
            # This route is for debugging configuration, so return error details.
            return jsonify({"ok": False, "error": str(exc)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)


