from fastapi import FastAPI, HTTPException, Query, Security, Path
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from datetime import datetime, timedelta
import os

app = FastAPI(default_response_class=JSONResponse)

# ------------------------------------------------------------------------------
# API Key Settings
# ------------------------------------------------------------------------------
API_KEY = "satyaprakashreddy6789"  # Your secret API key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(x_api_key: str = Security(api_key_header), api_key: str = Query(None)):
    provided_key = x_api_key or api_key
    if provided_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return provided_key

# ------------------------------------------------------------------------------
# In-Memory "Database" for Sensor Records
# ------------------------------------------------------------------------------
# We'll use a dictionary to simulate sensor records.
# The key is an auto-incremented integer ID.
records = {}
next_id = 1

# Preload a couple of sample records.
def preload_records():
    global next_id
    sample = [
        {"MachineID": "Machine1", "Timestamp": datetime.now() - timedelta(hours=1), "Temperature": 23.5, "Pressure": 1015.2},
        {"MachineID": "Machine2", "Timestamp": datetime.now() - timedelta(hours=2), "Temperature": 25.1, "Pressure": 1012.8},
    ]
    for rec in sample:
        rec["ID"] = next_id
        records[next_id] = rec
        next_id += 1

preload_records()

# ------------------------------------------------------------------------------
# GET: Retrieve All Records (or those within a time range)
# ------------------------------------------------------------------------------
@app.get("/records", response_class=JSONResponse)
def get_records(
    api_key: str = Security(get_api_key),
    start: str = Query(None, description="Start datetime in format YYYY-MM-DD HH:MM:SS"),
    end: str = Query(None, description="End datetime in format YYYY-MM-DD HH:MM:SS")
):
    # Get all records as a list.
    result = list(records.values())
    if start and end:
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")
        result = [rec for rec in result if start_dt <= rec["Timestamp"] <= end_dt]
    # Build a new list with formatted timestamps.
    formatted_result = []
    for rec in result:
        formatted_rec = rec.copy()
        if isinstance(formatted_rec["Timestamp"], datetime):
            formatted_rec["Timestamp"] = formatted_rec["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        # If it's already a string, assume it's formatted.
        formatted_result.append(formatted_rec)
    return {"status": "success", "data": formatted_result}

# ------------------------------------------------------------------------------
# POST: Create a New Sensor Record
# ------------------------------------------------------------------------------
@app.post("/records", response_class=JSONResponse)
def create_record(
    MachineID: str,
    Timestamp: str,
    Temperature: float,
    Pressure: float,
    api_key: str = Security(get_api_key)
):
    global next_id
    try:
        ts = datetime.strptime(Timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")
    record = {
        "ID": next_id,
        "MachineID": MachineID,
        "Timestamp": ts,
        "Temperature": Temperature,
        "Pressure": Pressure
    }
    records[next_id] = record
    next_id += 1
    # Prepare a copy with formatted timestamp.
    formatted_record = record.copy()
    formatted_record["Timestamp"] = formatted_record["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return {"status": "success", "record": formatted_record}

# ------------------------------------------------------------------------------
# PUT: Update an Existing Sensor Record
# ------------------------------------------------------------------------------
@app.put("/records/{record_id}", response_class=JSONResponse)
def update_record(
    record_id: int = Path(..., description="ID of the sensor record"),
    MachineID: str = None,
    Timestamp: str = None,
    Temperature: float = None,
    Pressure: float = None,
    api_key: str = Security(get_api_key)
):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    record = records[record_id]
    if MachineID is not None:
        record["MachineID"] = MachineID
    if Timestamp is not None:
        try:
            record["Timestamp"] = datetime.strptime(Timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")
    if Temperature is not None:
        record["Temperature"] = Temperature
    if Pressure is not None:
        record["Pressure"] = Pressure
    # Prepare a copy with formatted timestamp.
    formatted_record = record.copy()
    if isinstance(formatted_record["Timestamp"], datetime):
        formatted_record["Timestamp"] = formatted_record["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return {"status": "success", "record": formatted_record}

# ------------------------------------------------------------------------------
# DELETE: Remove a Sensor Record
# ------------------------------------------------------------------------------
@app.delete("/records/{record_id}", response_class=JSONResponse)
def delete_record(
    record_id: int = Path(..., description="ID of the sensor record"),
    api_key: str = Security(get_api_key)
):
    if record_id not in records:
        raise HTTPException(status_code=404, detail="Record not found")
    del records[record_id]
    return {"status": "success", "message": f"Record {record_id} deleted"}

# ------------------------------------------------------------------------------
# To Run:
# Save this file as records_api.py and run with:
#   uvicorn records_api:app --host 0.0.0.0 --port 8002 --reload
# ------------------------------------------------------------------------------
