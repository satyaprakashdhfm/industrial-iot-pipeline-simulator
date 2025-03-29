from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
import pyodbc
import os
from datetime import datetime, timedelta

app = FastAPI(default_response_class=JSONResponse)

# ---------------------------------------------------------------------------
# API Key Setup (Hardcoded)
# ---------------------------------------------------------------------------
API_KEY = "satyaprakashreddy6789"  # Your secret API key

# Set up the header-based API key extractor (auto_error=False to allow fallback)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(x_api_key: str = Depends(api_key_header), api_key: str = Query(None)):
    """
    Retrieve API key from header or query parameter.
    If not matching the expected key, raise 403.
    """
    provided_key = x_api_key or api_key
    if provided_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return provided_key

# ---------------------------------------------------------------------------
# Database Connection Settings
# ---------------------------------------------------------------------------
DB_SERVER = os.getenv("DB_SERVER", "localhost,1533")  # Include port if needed
DB_DATABASE = os.getenv("DB_DATABASE", "SensorDB")
DB_USERNAME = os.getenv("DB_USERNAME", "satya")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Satya@3479")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

def get_db_connection():
    conn_str = (
        f"DRIVER={DB_DRIVER};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)

# ---------------------------------------------------------------------------
# API Endpoint: Get Sensor Data (Default 24 Hours or Custom Range)
# ---------------------------------------------------------------------------
@app.get("/sensors", response_class=JSONResponse)
def fetch_sensors(
    start: str = Query(None, description="Start datetime in format YYYY-MM-DD HH:MM:SS"),
    end: str = Query(None, description="End datetime in format YYYY-MM-DD HH:MM:SS"),
    key: str = Depends(get_api_key)  # API key can come from header or query parameter
):
    # Determine the time range
    if not start or not end:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(hours=24)
    else:
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM:SS")

    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Build the SQL query
    query = f"""
        SELECT ID, MachineID, Timestamp, Temperature, Pressure
        FROM SensorData
        WHERE Timestamp BETWEEN '{start_str}' AND '{end_str}'
        ORDER BY Timestamp DESC
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [
            {
                "ID": row[0],
                "MachineID": row[1],
                "Timestamp": str(row[2]),
                "Temperature": row[3],
                "Pressure": row[4]
            }
            for row in rows
        ]

        return {
            "status": "success",
            "start_time": start_str,
            "end_time": end_str,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
