from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import requests
import json
from jinja2 import Environment, DictLoader
from datetime import datetime, timedelta
import statistics

app = FastAPI()

# ---------------------------------------------------------------------------
# API Integration Settings (Internal API key)
# ---------------------------------------------------------------------------
API_KEY = "satyaprakashreddy6789"
API_URL = "http://localhost:8001/sensors"

# ---------------------------------------------------------------------------
# In-Memory Jinja2 Templates (Dashboard)
# ---------------------------------------------------------------------------
templates_dict = {
    "layout.html": """
    <!DOCTYPE html>
    <html>
      <head>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" />
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
          body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
          h1, h2, h3, label { color: #ffcc00; }
          .card, .table { background-color: #1e1e1e !important; color: #e0e0e0 !important; }
          .table thead { background-color: #333; }
          .table thead th { color: #ffcc00; }
          .form-control, .btn { background-color: #333; border: 1px solid #444; color: #e0e0e0; }
          .btn:hover { background-color: #444; }
          .nav-link { color: #ffcc00 !important; }
          .nav-link:hover { color: #ffffff !important; }
          .summary-card { border: 1px solid #444; padding: 15px; margin-bottom: 20px; border-radius: 5px; background-color: #1e1e1e; }
        </style>
      </head>
      <body>
        <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #000;">
          <div class="container-fluid">
            <a class="navbar-brand" href="/cyberpunk">Cyberpunk Dashboard</a>
          </div>
        </nav>
        <div class="container my-4">
          {% block content %}{% endblock %}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
      </body>
    </html>
    """,
    "cyberpunk.html": """
    {% extends "layout.html" %}
    {% block content %}
    <h1 class="mb-4">Cyberpunk Dashboard</h1>
    <!-- Filter Form -->
    <form method="get" class="row g-3 align-items-end">
      <div class="col-auto">
        <label for="start" class="form-label">Start Time</label>
        <input type="datetime-local" class="form-control" name="start" id="start" value="{{ start_value|default('') }}">
      </div>
      <div class="col-auto">
        <label for="end" class="form-label">End Time</label>
        <input type="datetime-local" class="form-control" name="end" id="end" value="{{ end_value|default('') }}">
      </div>
      <div class="col-auto">
        <button type="submit" class="btn">Filter</button>
      </div>
    </form>
    <p class="text-muted">If left blank, data from the last 24 hours is displayed.</p>
    <!-- Summary Cards -->
    <div class="row">
      <div class="col-md-6">
        <div class="summary-card">
          <h3>Machine1 Summary</h3>
          <p>Temperature - Avg: <strong>{{ m1_avg_temp }}</strong>, Min: <strong>{{ m1_min_temp }}</strong>, Max: <strong>{{ m1_max_temp }}</strong></p>
          <p>Pressure - Avg: <strong>{{ m1_avg_press }}</strong>, Min: <strong>{{ m1_min_press }}</strong>, Max: <strong>{{ m1_max_press }}</strong></p>
        </div>
      </div>
      <div class="col-md-6">
        <div class="summary-card">
          <h3>Machine2 Summary</h3>
          <p>Temperature - Avg: <strong>{{ m2_avg_temp }}</strong>, Min: <strong>{{ m2_min_temp }}</strong>, Max: <strong>{{ m2_max_temp }}</strong></p>
          <p>Pressure - Avg: <strong>{{ m2_avg_press }}</strong>, Min: <strong>{{ m2_min_press }}</strong>, Max: <strong>{{ m2_max_press }}</strong></p>
        </div>
      </div>
    </div>
    <!-- Charts -->
    <div class="row my-4">
      <div class="col-md-12">
        <div class="card p-3">
          <h4>Temperature Over Time</h4>
          <canvas id="tempChart"></canvas>
        </div>
      </div>
    </div>
    <div class="row my-4">
      <div class="col-md-12">
        <div class="card p-3">
          <h4>Pressure Over Time</h4>
          <canvas id="pressChart"></canvas>
        </div>
      </div>
    </div>
    <script>
      const timeLabels = {{ time_labels|safe }};
      const m1Temps = {{ m1_temps|safe }};
      const m2Temps = {{ m2_temps|safe }};
      const m1Press = {{ m1_press|safe }};
      const m2Press = {{ m2_press|safe }};
      const ctxTemp = document.getElementById('tempChart').getContext('2d');
      new Chart(ctxTemp, {
        type: 'line',
        data: {
          labels: timeLabels,
          datasets: [
            { label: 'Machine1 Temperature (°C)', data: m1Temps, borderColor: '#ffcc00', backgroundColor: 'rgba(255,204,0,0.1)', fill: true, tension: 0.2 },
            { label: 'Machine2 Temperature (°C)', data: m2Temps, borderColor: '#00ccff', backgroundColor: 'rgba(0,204,255,0.1)', fill: true, tension: 0.2 }
          ]
        },
        options: { responsive: true, scales: { x: { ticks: { color: '#e0e0e0' }, grid: { color: '#444' } }, y: { ticks: { color: '#e0e0e0' }, grid: { color: '#444' } } }, plugins: { legend: { labels: { color: '#ffcc00' } } } }
      });
      const ctxPress = document.getElementById('pressChart').getContext('2d');
      new Chart(ctxPress, {
        type: 'line',
        data: {
          labels: timeLabels,
          datasets: [
            { label: 'Machine1 Pressure (hPa)', data: m1Press, borderColor: '#ff6600', backgroundColor: 'rgba(255,102,0,0.1)', fill: true, tension: 0.2 },
            { label: 'Machine2 Pressure (hPa)', data: m2Press, borderColor: '#66ff66', backgroundColor: 'rgba(102,255,102,0.1)', fill: true, tension: 0.2 }
          ]
        },
        options: { responsive: true, scales: { x: { ticks: { color: '#e0e0e0' }, grid: { color: '#444' } }, y: { ticks: { color: '#e0e0e0' }, grid: { color: '#444' } } }, plugins: { legend: { labels: { color: '#ffcc00' } } } }
      });
    </script>
    {% endblock %}
    """
}

env = Environment(loader=DictLoader(templates_dict))

def render_template(template_name: str, context: dict):
    template = env.get_template(template_name)
    return template.render(**context)

# ---------------------------------------------------------------------------
# Cyberpunk Dashboard Endpoint
# ---------------------------------------------------------------------------
@app.get("/cyberpunk", response_class=HTMLResponse)
def cyberpunk_dashboard(request: Request, start: str = None, end: str = None):
    """
    Displays a dashboard for sensor data fetched via an API.
    Date format must be "YYYY-MM-DD HH:MM:SS".
    """
    # Default to last 24 hours if no start or end provided.
    if not start or not end:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(hours=24)
    else:
        # Replace any 'T' with a space so the format matches "YYYY-MM-DD HH:MM:SS"
        start = start.replace("T", " ")
        end = end.replace("T", " ")
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return HTMLResponse(content="<h1>Invalid date format. Use YYYY-MM-DD HH:MM:SS</h1>", status_code=400)

    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    # -----------------------------------------------------------------------
    # Fetch sensor data from the API using proper headers and parameters.
    # -----------------------------------------------------------------------
    try:
        headers = {"X-API-KEY": API_KEY}
        params = {"start": start_str, "end": end_str}
        api_response = requests.get(API_URL, headers=headers, params=params)
        api_response.raise_for_status()
        sensor_data = api_response.json()

        # If the response is a string, attempt to parse it.
        if isinstance(sensor_data, str):
            sensor_data = json.loads(sensor_data)
        
        # If the sensor API returns a dict with a "data" key, use that.
        if isinstance(sensor_data, dict) and "data" in sensor_data:
            sensor_data = sensor_data["data"]
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: Failed to retrieve sensor data: {str(e)}</h1>", status_code=500)

    # Ensure sensor_data is a list.
    if not isinstance(sensor_data, list):
        return HTMLResponse(content="<h1>Error: Unexpected sensor data format</h1>", status_code=500)

    # Split sensor data by MachineID.
    rows_m1 = [record for record in sensor_data if record.get("MachineID") == "Machine1"]
    rows_m2 = [record for record in sensor_data if record.get("MachineID") == "Machine2"]

    def process_rows(rows):
        data, times, temps, press = [], [], [], []
        for r in rows:
            record = {
                "ID": r.get("ID"),
                "MachineID": r.get("MachineID"),
                "Timestamp": r.get("Timestamp"),
                "Temperature": float(r.get("Temperature")),
                "Pressure": float(r.get("Pressure"))
            }
            data.append(record)
            times.append(record["Timestamp"])
            temps.append(record["Temperature"])
            press.append(record["Pressure"])
        return data, times, temps, press

    m1_data, m1_times, m1_temps, m1_press = process_rows(rows_m1)
    m2_data, m2_times, m2_temps, m2_press = process_rows(rows_m2)
    time_labels = m1_times if m1_times else m2_times

    def compute_stats(values):
        if values:
            return round(statistics.mean(values), 2), round(min(values), 2), round(max(values), 2)
        return 0, 0, 0

    m1_avg_temp, m1_min_temp, m1_max_temp = compute_stats(m1_temps)
    m1_avg_press, m1_min_press, m1_max_press = compute_stats(m1_press)
    m2_avg_temp, m2_min_temp, m2_max_temp = compute_stats(m2_temps)
    m2_avg_press, m2_min_press, m2_max_press = compute_stats(m2_press)

    context = {
        "title": "Cyberpunk Dashboard",
        "start_value": start_str,
        "end_value": end_str,
        "machine1_rows": m1_data,
        "machine2_rows": m2_data,
        "time_labels": time_labels,
        "m1_temps": m1_temps,
        "m2_temps": m2_temps,
        "m1_press": m1_press,
        "m2_press": m2_press,
        "m1_avg_temp": m1_avg_temp, "m1_min_temp": m1_min_temp, "m1_max_temp": m1_max_temp,
        "m1_avg_press": m1_avg_press, "m1_min_press": m1_min_press, "m1_max_press": m1_max_press,
        "m2_avg_temp": m2_avg_temp, "m2_min_temp": m2_min_temp, "m2_max_temp": m2_max_temp,
        "m2_avg_press": m2_avg_press, "m2_min_press": m2_min_press, "m2_max_press": m2_max_press,
    }

    return HTMLResponse(content=render_template("cyberpunk.html", context))
