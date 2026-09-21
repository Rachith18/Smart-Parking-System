import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# ORACLE XE 11G - THICK MODE
# =========================================================
# Set ORACLE_CLIENT_LIB_DIR in .env to your Oracle XE 11g bin folder.
# Example:
# C:\oraclexe\app\oracle\product\11.2.0\server\bin

ORACLE_CLIENT_LIB_DIR = os.getenv(
    "ORACLE_CLIENT_LIB_DIR",
    r"C:\oraclexe\app\oracle\product\11.2.0\server\bin"
)

if os.path.isdir(ORACLE_CLIENT_LIB_DIR):
    try:
        oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_LIB_DIR)
    except oracledb.ProgrammingError:
        # Client may already have been initialized.
        pass

DB_USER = os.getenv("DB_USER", "system")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DSN = os.getenv("DB_DSN", "localhost:1521/XE")


def get_connection():
    """Create and return an Oracle database connection."""
    if not DB_PASSWORD:
        raise RuntimeError(
            "DB_PASSWORD is not configured. Create a .env file from .env.example."
        )

    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN,
    )


def get_parking_slots():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT slot_id, slot_number, status, vehicle_number
            FROM parking_slots
            ORDER BY slot_id
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def reserve_slot(slot_id, vehicle_number):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT slot_number
            FROM parking_slots
            WHERE slot_id = :slot_id
        """, {"slot_id": slot_id})

        result = cursor.fetchone()
        if result is None:
            return False

        slot_number = result[0]

        cursor.execute("""
            UPDATE parking_slots
            SET status = 'OCCUPIED',
                vehicle_number = :vehicle_number
            WHERE slot_id = :slot_id
              AND status = 'AVAILABLE'
        """, {
            "vehicle_number": vehicle_number,
            "slot_id": slot_id,
        })

        if cursor.rowcount == 0:
            connection.rollback()
            return False

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
            "vehicle_number": vehicle_number,
        })

        connection.commit()
        return True
    except Exception as exc:
        connection.rollback()
        print("Error reserving slot:", exc)
        return False
    finally:
        cursor.close()
        connection.close()


def release_slot(slot_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT slot_number
            FROM parking_slots
            WHERE slot_id = :slot_id
        """, {"slot_id": slot_id})

        result = cursor.fetchone()
        if result is None:
            return False

        slot_number = result[0]

        cursor.execute("""
            UPDATE parking_slots
            SET status = 'AVAILABLE',
                vehicle_number = NULL
            WHERE slot_id = :slot_id
              AND status = 'OCCUPIED'
        """, {"slot_id": slot_id})

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        cursor.execute("""
            UPDATE parking_history
            SET exit_time = SYSTIMESTAMP,
                status = 'COMPLETED'
            WHERE history_id = (
                SELECT MAX(history_id)
                FROM parking_history
                WHERE slot_number = :slot_number
                  AND exit_time IS NULL
            )
        """, {"slot_number": slot_number})

        connection.commit()
        return True
    except Exception as exc:
        connection.rollback()
        print("Error releasing slot:", exc)
        return False
    finally:
        cursor.close()
        connection.close()


def get_parking_history():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT history_id, slot_number, vehicle_number,
                   entry_time, exit_time, status
            FROM parking_history
            ORDER BY history_id DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def search_vehicle(vehicle_number):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT history_id, slot_number, vehicle_number,
                   entry_time, exit_time, status
            FROM parking_history
            WHERE UPPER(vehicle_number) = UPPER(:vehicle_number)
            ORDER BY history_id DESC
        """, {"vehicle_number": vehicle_number})
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


def authenticate_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT user_id, username, role
            FROM parking_users
            WHERE username = :username
              AND password = :password
        """, {
            "username": username,
            "password": password,
        })
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def add_parking_slot(slot_number):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*)
            FROM parking_slots
            WHERE UPPER(slot_number) = UPPER(:slot_number)
        """, {"slot_number": slot_number})

        if cursor.fetchone()[0] > 0:
            return False

        cursor.execute("""
            SELECT NVL(MAX(slot_id), 0) + 1
            FROM parking_slots
        """)
        new_slot_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO parking_slots (slot_id, slot_number, status, vehicle_number)
            VALUES (:slot_id, :slot_number, 'AVAILABLE', NULL)
        """, {
            "slot_id": new_slot_id,
            "slot_number": slot_number,
        })

        connection.commit()
        return True
    except Exception as exc:
        connection.rollback()
        print("Error adding parking slot:", exc)
        return False
    finally:
        cursor.close()
        connection.close()


def delete_parking_slot(slot_id):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT status
            FROM parking_slots
            WHERE slot_id = :slot_id
        """, {"slot_id": slot_id})

        result = cursor.fetchone()
        if result is None or result[0] == "OCCUPIED":
            return False

        cursor.execute("""
            DELETE FROM parking_slots
            WHERE slot_id = :slot_id
        """, {"slot_id": slot_id})

        connection.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        connection.rollback()
        print("Error deleting parking slot:", exc)
        return False
    finally:
        cursor.close()
        connection.close()
