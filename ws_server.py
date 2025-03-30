from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
import aioodbc
import asyncio
from datetime import datetime

app = FastAPI()

# MSSQL Database Configuration
DB_CONFIG = {
    "dsn": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1533;DATABASE=SensorDB;UID=satya;PWD=Satya@3479"
}

# Query to fetch the most recent 10 records
QUERY = "SELECT TOP 10 * FROM SensorData ORDER BY Timestamp DESC"

# Track the last known state of data
last_snapshot = []


# Convert datetime to string for JSON serialization
def serialize_row(row, description):
    row_dict = dict(zip([column[0] for column in description], row))
    # Convert datetime objects to ISO format
    for key, value in row_dict.items():
        if isinstance(value, datetime):
            row_dict[key] = value.isoformat()
    return row_dict


# Fetch data from database
async def fetch_data():
    async with aioodbc.create_pool(dsn=DB_CONFIG["dsn"], minsize=1, maxsize=5) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(QUERY)
                rows = await cur.fetchall()
                if not rows:
                    return []
                return [serialize_row(row, cur.description) for row in rows]


# Get only new/updated records
def get_updates(new_data, last_data):
    if not last_data:
        return new_data  # Send all data if it's the first fetch

    # Send only the new/updated records by comparing last snapshot
    new_set = {tuple(d.items()) for d in new_data}
    last_set = {tuple(d.items()) for d in last_data}

    updates = [dict(record) for record in (new_set - last_set)]
    return updates


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global last_snapshot
    await websocket.accept()
    try:
        while True:
            new_data = await fetch_data()
            updates = get_updates(new_data, last_snapshot)

            # Send only new or updated records
            if updates:
                last_snapshot = new_data
                await websocket.send_json(updates)

            # Poll every 0.1 second (optimized delay for real-time updates)
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error: {e}")
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close()
            except RuntimeError:
                print("WebSocket already closed, skipping...")


@app.get("/")
async def read_root():
    return {"message": "WebSocket ready at /ws"}
