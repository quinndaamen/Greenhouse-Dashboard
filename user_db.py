import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_sensors"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_input (
        id INT AUTO_INCREMENT PRIMARY KEY,
        uTemp FLOAT,
        uHumidity FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def save_user_settings(uTemp, uHumidity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_input (uTemp, uHumidity) VALUES (%s, %s)", (uTemp, uHumidity))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved settings: Temp={uTemp}, Humidity={uHumidity}")

def get_latest_settings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT uTemp, uHumidity FROM user_input ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result 
    return None
