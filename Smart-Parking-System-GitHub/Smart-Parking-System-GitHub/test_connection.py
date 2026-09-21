from database import get_connection

try:
    connection = get_connection()

    print("Oracle Database connected successfully!")

    cursor = connection.cursor()
    cursor.execute("SELECT SYSDATE FROM dual")

    result = cursor.fetchone()
    print("Oracle Server Date:", result[0])

    cursor.close()
    connection.close()

except Exception as e:
    print("Database connection failed.")
    print("Error:", e)