import sqlite3
from datetime import datetime, timedelta
connection = sqlite3.connect("bookings.db")

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.sort_keys = False
connection.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        booking_date TEXT NOT NULL,
        start_hour INTEGER NOT NULL CHECK (start_hour BETWEEN 0 AND 23),
        duration_hours INTEGER NOT NULL CHECK (duration_hours >= 1)
    )
""")

connection.commit()
connection.close()

@app.get("/bookings")
def get_bookings():
    connection = sqlite3.connect("bookings.db")
    try:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM bookings ORDER BY id").fetchall()
        bookings = [dict(row) for row in rows]
        for booking in bookings:
            starts_at = datetime.strptime(booking["booking_date"], "%Y-%m-%d")
            starts_at = starts_at.replace(hour=booking["start_hour"])
            ends_at = starts_at + timedelta(hours=booking["duration_hours"])
            booking["end_at"] = ends_at.isoformat(sep=" ", timespec="minutes")
        return jsonify(bookings)
    finally:
        connection.close()


def has_overlap(connection, starts_at, ends_at, exclude_id=None):
    bookings = connection.execute(
        "SELECT id, booking_date, start_hour, duration_hours FROM bookings"
    ).fetchall()

    for booking in bookings:
        if booking["id"] == exclude_id:
            continue

        booked_start = datetime.strptime(booking["booking_date"], "%Y-%m-%d")
        booked_start = booked_start.replace(hour=booking["start_hour"])
        booked_end = booked_start + timedelta(hours=booking["duration_hours"])

        if starts_at < booked_end and booked_start < ends_at:
            return True

    return False
@app.post("/bookings/add")
def add_booking():
    customer_name = request.form.get("customer_name", "").strip()
    booking_date = request.form.get("booking_date", "").strip()
    start_hour = request.form.get("start_hour", "").strip()
    duration_hours = request.form.get("duration_hours", "").strip()
    if not customer_name:

        return jsonify({"message": "Customer name is required."}), 400
    try:
        start_hour = int(start_hour)
        duration_hours = int(duration_hours)

    except ValueError:
        return jsonify({"message": "Start hour and duration must be whole numbers."}), 400
    
    if start_hour < 0 or start_hour > 23:
        return jsonify({"message": "Start hour must be between 0 and 23."}), 400

    if duration_hours < 1: 
          return jsonify({"Duration must be at least one hour"}), 400
    try:
        starts_at = datetime.strptime(booking_date, "%Y-%m-%d")
        starts_at = starts_at.replace(hour=start_hour)
    except ValueError:
        return jsonify({"message": "Enter a valid date in YYYY-MM-DD format."}), 400
    try:
        ends_at = starts_at + timedelta(hours=duration_hours)
    except OverflowError:
        return jsonify({"message": "Booking end date is out of range."}), 400

  
    booking_values = (customer_name, starts_at.date().isoformat(), start_hour, duration_hours)

    
    connection = sqlite3.connect("bookings.db")
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.row_factory = sqlite3.Row
        if has_overlap(connection, starts_at, ends_at):
          return jsonify({"message": "This time is already booked."}), 409

        connection.execute(
            """
            INSERT INTO bookings (customer_name, booking_date, start_hour, duration_hours)
            VALUES (?, ?, ?, ?)
            """,
            booking_values
        )
        connection.commit()
    finally:
        connection.close()
    
    
    return jsonify({
        "message": "Data received successfully.",
        "customer_name": customer_name,
        "booking_date": booking_date,
        "start_hour": start_hour,
        "end_at": ends_at.isoformat(sep=" ", timespec="minutes"),
        "duration_hours": duration_hours
    })

@app.post("/bookings/<int:booking_id>/delete")
def delete_booking(booking_id):
    connection = sqlite3.connect("bookings.db")
    try:
        result = connection.execute(
            "DELETE FROM bookings WHERE id = ?",
            (booking_id,)
        )

        if result.rowcount == 0:
            return jsonify({"message": "Booking not found."}), 404

        connection.commit()
        return jsonify({"message": "Booking deleted successfully."})
    finally:
        connection.close()

@app.post("/bookings/<int:booking_id>/edit")
def edit_booking(booking_id):
    booking_date = request.form.get("booking_date", "").strip()

    try:
        start_hour = int(request.form.get("start_hour", ""))
        duration_hours = int(request.form.get("duration_hours", ""))

        if duration_hours < 1:
            return jsonify({"message": "Duration must be at least one hour."}), 400

        starts_at = datetime.strptime(booking_date, "%Y-%m-%d")
        starts_at = starts_at.replace(hour=start_hour)
        ends_at = starts_at + timedelta(hours=duration_hours)
    except (ValueError, OverflowError):
        return jsonify({"message": "Enter a valid date, start hour, and duration."}), 400

    connection = sqlite3.connect("bookings.db")
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.row_factory = sqlite3.Row

        booking = connection.execute(
            "SELECT id FROM bookings WHERE id = ?", (booking_id,)
        ).fetchone()

        if booking is None:
            return jsonify({"message": "Booking not found."}), 404

        if has_overlap(connection, starts_at, ends_at, exclude_id=booking_id):
            return jsonify({"message": "This time is already booked."}), 409

        connection.execute(
            """
            UPDATE bookings
            SET booking_date = ?, start_hour = ?, duration_hours = ?
            WHERE id = ?
            """,
            (starts_at.date().isoformat(), start_hour, duration_hours, booking_id)
        )
        connection.commit()
        return jsonify({"message": "Booking updated successfully."})
    finally:
        connection.close()        
if __name__ == "__main__":
    app.run(port=5050)
