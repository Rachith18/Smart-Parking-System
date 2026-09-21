import oracledb


# =========================================================
# ORACLE XE 11G - THICK MODE
# =========================================================

oracledb.init_oracle_client(
    lib_dir=r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"
)


DB_USER = "system"
DB_PASSWORD = "1234"
DB_DSN = "localhost:1521/XE"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )


# =========================================================
# GET ALL PARKING SLOTS
# =========================================================

def get_parking_slots():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                slot_id,
                slot_number,
                status,
                vehicle_number
            FROM parking_slots
            ORDER BY slot_id
        """)

        slots = cursor.fetchall()

        return slots

    finally:

        cursor.close()
        connection.close()


# =========================================================
# RESERVE PARKING SLOT
# =========================================================

def reserve_slot(slot_id, vehicle_number):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Get slot number
        cursor.execute("""
            SELECT slot_number
            FROM parking_slots
            WHERE slot_id = :slot_id
        """, {
            "slot_id": slot_id
        })

        result = cursor.fetchone()

        if result is None:
            return False

        slot_number = result[0]

        # Reserve the slot
        cursor.execute("""
            UPDATE parking_slots
            SET
                status = 'OCCUPIED',
                vehicle_number = :vehicle_number
            WHERE slot_id = :slot_id
              AND status = 'AVAILABLE'
        """, {
            "vehicle_number": vehicle_number,
            "slot_id": slot_id
        })

        # Slot was already occupied
        if cursor.rowcount == 0:

            connection.rollback()

            return False

        # Add parking history
        cursor.execute("""
            INSERT INTO parking_history
            (
                history_id,
                slot_number,
                vehicle_number,
                entry_time,
                exit_time,
                status
            )
            VALUES
            (
                parking_history_seq.NEXTVAL,
                :slot_number,
                :vehicle_number,
                SYSTIMESTAMP,
                NULL,
                'PARKED'
            )
        """, {
            "slot_number": slot_number,
            "vehicle_number": vehicle_number
        })

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print("Error reserving slot:", e)

        return False

    finally:

        cursor.close()
        connection.close()


# =========================================================
# RELEASE PARKING SLOT
# =========================================================

def release_slot(slot_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Get slot number
        cursor.execute("""
            SELECT slot_number
            FROM parking_slots
            WHERE slot_id = :slot_id
        """, {
            "slot_id": slot_id
        })

        result = cursor.fetchone()

        if result is None:
            return False

        slot_number = result[0]

        # Make slot available
        cursor.execute("""
            UPDATE parking_slots
            SET
                status = 'AVAILABLE',
                vehicle_number = NULL
            WHERE slot_id = :slot_id
        """, {
            "slot_id": slot_id
        })

        # Complete active history record
        cursor.execute("""
            UPDATE parking_history
            SET
                exit_time = SYSTIMESTAMP,
                status = 'COMPLETED'
            WHERE history_id = (
                SELECT MAX(history_id)
                FROM parking_history
                WHERE slot_number = :slot_number
                  AND exit_time IS NULL
            )
        """, {
            "slot_number": slot_number
        })

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print("Error releasing slot:", e)

        return False

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET PARKING HISTORY
# =========================================================

def get_parking_history():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                history_id,
                slot_number,
                vehicle_number,
                entry_time,
                exit_time,
                status
            FROM parking_history
            ORDER BY history_id DESC
        """)

        history = cursor.fetchall()

        return history

    finally:

        cursor.close()
        connection.close()


# =========================================================
# SEARCH VEHICLE
# =========================================================

def search_vehicle(vehicle_number):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                history_id,
                slot_number,
                vehicle_number,
                entry_time,
                exit_time,
                status
            FROM parking_history
            WHERE UPPER(vehicle_number) = UPPER(:vehicle_number)
            ORDER BY history_id DESC
        """, {
            "vehicle_number": vehicle_number
        })

        records = cursor.fetchall()

        return records

    finally:

        cursor.close()
        connection.close()


# =========================================================
# AUTHENTICATE USER
# =========================================================

def authenticate_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                user_id,
                username,
                role
            FROM parking_users
            WHERE username = :username
              AND password = :password
        """, {
            "username": username,
            "password": password
        })

        user = cursor.fetchone()

        return user

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADD PARKING SLOT
# =========================================================

def add_parking_slot(slot_number):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check whether slot already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM parking_slots
            WHERE UPPER(slot_number) = UPPER(:slot_number)
        """, {
            "slot_number": slot_number
        })

        count = cursor.fetchone()[0]

        if count > 0:

            print("Slot already exists.")

            return False

        # Generate next slot ID
        cursor.execute("""
            SELECT NVL(MAX(slot_id), 0) + 1
            FROM parking_slots
        """)

        new_slot_id = cursor.fetchone()[0]

        # Insert new slot
        cursor.execute("""
            INSERT INTO parking_slots
            (
                slot_id,
                slot_number,
                status,
                vehicle_number
            )
            VALUES
            (
                :slot_id,
                :slot_number,
                'AVAILABLE',
                NULL
            )
        """, {
            "slot_id": new_slot_id,
            "slot_number": slot_number
        })

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print("Error adding parking slot:", e)

        return False

    finally:

        cursor.close()
        connection.close()


# =========================================================
# DELETE PARKING SLOT
# =========================================================

def delete_parking_slot(slot_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check slot
        cursor.execute("""
            SELECT status
            FROM parking_slots
            WHERE slot_id = :slot_id
        """, {
            "slot_id": slot_id
        })

        result = cursor.fetchone()

        if result is None:

            return False

        # Do not delete occupied slot
        if result[0] == "OCCUPIED":

            print("Cannot delete an occupied slot.")

            return False

        # Delete slot
        cursor.execute("""
            DELETE FROM parking_slots
            WHERE slot_id = :slot_id
        """, {
            "slot_id": slot_id
        })

        connection.commit()

        return True

    except Exception as e:

        connection.rollback()

        print("Error deleting parking slot:", e)

        return False

    finally:

        cursor.close()
        connection.close()