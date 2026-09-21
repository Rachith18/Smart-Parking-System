from flask import Flask, render_template, request, redirect, url_for, session, flash

from database import (
    get_parking_slots,
    reserve_slot,
    release_slot,
    get_parking_history,
    search_vehicle,
    authenticate_user
)

app = Flask(__name__)
app.secret_key = "smart-parking-secret-key"


# =========================================================
# LOGIN
# =========================================================

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

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return redirect(url_for("dashboard"))


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    slots = get_parking_slots()

    total_slots = len(slots)

    available_slots = sum(
        1 for slot in slots
        if str(slot[2]).upper() == "AVAILABLE"
    )

    occupied_slots = sum(
        1 for slot in slots
        if str(slot[2]).upper() == "OCCUPIED"
    )

    records = get_parking_history()

    # Count currently occupied vehicles
    total_vehicles = occupied_slots

    return render_template(
        "dashboard.html",
        total_slots=total_slots,
        available_slots=available_slots,
        occupied_slots=occupied_slots,
        total_vehicles=total_vehicles
    )


# =========================================================
# PARKING SLOTS
# =========================================================

@app.route("/parking")
def parking():

    if "user_id" not in session:
        return redirect(url_for("login"))

    slots = get_parking_slots()

    available_slots = sum(
        1 for slot in slots
        if str(slot[2]).upper() == "AVAILABLE"
    )

    return render_template(
        "parking.html",
        slots=slots,
        available_slots=available_slots
    )


# =========================================================
# RESERVE SLOT
# =========================================================

@app.route("/reserve/<int:slot_id>", methods=["POST"])
def reserve(slot_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    vehicle_number = request.form.get("vehicle_number", "").strip()

    if not vehicle_number:
        flash("Please enter vehicle number.")
        return redirect(url_for("parking"))

    success = reserve_slot(slot_id, vehicle_number)

    if success:
        flash(
            f"Slot {slot_id} reserved successfully for {vehicle_number}."
        )
    else:
        flash(
            "Unable to reserve this slot. It may already be occupied."
        )

    return redirect(url_for("parking"))


# =========================================================
# RELEASE SLOT
# =========================================================

@app.route("/release/<int:slot_id>", methods=["POST"])
def release(slot_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    success = release_slot(slot_id)

    if success:
        flash("Parking slot released successfully.")
    else:
        flash("Unable to release the parking slot.")

    return redirect(url_for("parking"))


# =========================================================
# PARKING HISTORY
# =========================================================

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    records = get_parking_history()

    return render_template(
        "history.html",
        records=records
    )


# =========================================================
# SEARCH VEHICLE
# =========================================================

@app.route("/search", methods=["GET", "POST"])
def search():

    if "user_id" not in session:
        return redirect(url_for("login"))

    records = []
    vehicle_number = ""

    if request.method == "POST":

        vehicle_number = request.form.get(
            "vehicle_number",
            ""
        ).strip()

        if vehicle_number:
            records = search_vehicle(vehicle_number)

    return render_template(
        "search.html",
        records=records,
        vehicle_number=vehicle_number
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )