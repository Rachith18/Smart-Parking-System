import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

from database import (
    get_parking_slots,
    reserve_slot,
    release_slot,
    get_parking_history,
    search_vehicle,
    authenticate_user,
    add_parking_slot,
    delete_parking_slot,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")


def login_required():
    return "user_id" in session


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = authenticate_user(username, password)

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[2]
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/")
def home():
    if not login_required():
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    slots = get_parking_slots()
    total_slots = len(slots)
    available_slots = sum(1 for slot in slots if str(slot[2]).upper() == "AVAILABLE")
    occupied_slots = sum(1 for slot in slots if str(slot[2]).upper() == "OCCUPIED")

    return render_template(
        "dashboard.html",
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        total_vehicles=occupied_slots,
    )


@app.route("/parking")
def parking():
    if not login_required():
        return redirect(url_for("login"))

    slots = get_parking_slots()
    available_slots = sum(1 for slot in slots if str(slot[2]).upper() == "AVAILABLE")
    return render_template("index.html", slots=slots, available_slots=available_slots)


@app.route("/reserve/<int:slot_id>", methods=["POST"])
def reserve(slot_id):
    if not login_required():
        return redirect(url_for("login"))

    vehicle_number = request.form.get("vehicle_number", "").strip().upper()
    if not vehicle_number:
        flash("Please enter vehicle number.")
        return redirect(url_for("parking"))

    if reserve_slot(slot_id, vehicle_number):
        flash(f"Slot {slot_id} reserved successfully for {vehicle_number}.")
    else:
        flash("Unable to reserve this slot. It may already be occupied.")

    return redirect(url_for("parking"))


@app.route("/release/<int:slot_id>", methods=["POST"])
def release(slot_id):
    if not login_required():
        return redirect(url_for("login"))

    if release_slot(slot_id):
        flash("Parking slot released successfully.")
    else:
        flash("Unable to release the parking slot.")

    return redirect(url_for("parking"))


@app.route("/history")
def history():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("history.html", records=get_parking_history())


@app.route("/search", methods=["GET", "POST"])
def search():
    if not login_required():
        return redirect(url_for("login"))

    records = []
    vehicle_number = ""
    if request.method == "POST":
        vehicle_number = request.form.get("vehicle_number", "").strip().upper()
        if vehicle_number:
            records = search_vehicle(vehicle_number)

    return render_template("search.html", records=records, vehicle_number=vehicle_number)


@app.route("/admin")
def admin():
    if not login_required():
        return redirect(url_for("login"))

    if str(session.get("role", "")).upper() != "ADMIN":
        flash("Admin access is required.")
        return redirect(url_for("dashboard"))

    slots = get_parking_slots()
    total_slots = len(slots)
    available_slots = sum(1 for slot in slots if str(slot[2]).upper() == "AVAILABLE")
    occupied_slots = sum(1 for slot in slots if str(slot[2]).upper() == "OCCUPIED")

    return render_template(
        "admin.html",
        slots=slots,
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
    )


@app.route("/admin/add-slot", methods=["POST"])
def add_slot():
    if not login_required():
        return redirect(url_for("login"))
    if str(session.get("role", "")).upper() != "ADMIN":
        flash("Admin access is required.")
        return redirect(url_for("dashboard"))

    slot_number = request.form.get("slot_number", "").strip().upper()
    if not slot_number:
        flash("Enter a slot number.")
    elif add_parking_slot(slot_number):
        flash(f"Parking slot {slot_number} added successfully.")
    else:
        flash(f"Parking slot {slot_number} already exists or could not be added.")

    return redirect(url_for("admin"))


@app.route("/admin/delete-slot/<int:slot_id>", methods=["POST"])
def delete_slot(slot_id):
    if not login_required():
        return redirect(url_for("login"))
    if str(session.get("role", "")).upper() != "ADMIN":
        flash("Admin access is required.")
        return redirect(url_for("dashboard"))

    if delete_parking_slot(slot_id):
        flash("Parking slot deleted successfully.")
    else:
        flash("Cannot delete the slot. Check whether it exists or is occupied.")

    return redirect(url_for("admin"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
