from fastapi import FastAPI
import pyodbc
import os

app = FastAPI()

# Database connection settings
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_DATABASE = os.getenv("DB_DATABASE", "SensorDB")
DB_USERNAME = os.getenv("DB_USERNAME", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Scam@1992")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Function to get database connection
def get_db_connection():
    conn_str = f"DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD};"
    return pyodbc.connect(conn_str)

@app.get("/")
def home():
    return {"message": "FastAPI is running!"}
@app.get("/testdb")
def test_database_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Simple query to check connection
        cursor.fetchall()  # Ensure query executes
        cursor.close()
        conn.close()
        return {"status": "success", "message": "Database connection successful!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/last-24-hours")
def get_last_24_hours_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM SensorData WHERE Timestamp >= DATEADD(HOUR, -24, GETDATE());"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        result = [
            {"ID": row[0], "MachineID": row[1], "Timestamp": row[2], "Temperature": row[3], "Pressure": row[4]}
            for row in data
        ]
        return {"status": "success", "data": result}

    except Exception as e:
        return {"status": "error", "message": str(e)}
 
