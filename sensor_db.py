from datetime import datetime, timedelta
import mysql.connector

def init_db():
    conn = mysql.connector.connect(
        host='localhost', user='root', password='', database='db_sensors'
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            aTemp FLOAT,
            aHumidity FLOAT,
            aLight FLOAT,
            timeStamp DATETIME
        )
    """)
    conn.commit()
    conn.close()
    print(" Database created")

def insert_sensor_data(aTemp, aHumidity, aLight):
    conn = mysql.connector.connect(
        host='localhost', user='root', password='', database='db_sensors'
    )
    cursor = conn.cursor()

    cursor.execute("SELECT timeStamp FROM sensors ORDER BY timeStamp DESC LIMIT 1")
    last_row = cursor.fetchone()
    now = datetime.now()

    if not last_row or (now - last_row[0]) >= timedelta(minutes=1):
        sql = "INSERT INTO sensors (aTemp, aHumidity, aLight, timeStamp) VALUES (%s, %s, %s, %s)"
        val = (aTemp, aHumidity, aLight, now)
        cursor.execute(sql, val)
        conn.commit()
        print(f"✅ Data inserted at {now.strftime('%H:%M:%S')}")
    else:
        print("⏸ Skipped — last entry less than 1 minute ago")

    conn.close()

def fetch_sensor_data(limit=100):
    conn = mysql.connector.connect(
        host='localhost', user='root', password='', database='db_sensors'
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timeStamp, aTemp, aHumidity, aLight FROM sensors ORDER BY timeStamp DESC LIMIT %s",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
