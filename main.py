from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import pyodbc
import os
from datetime import datetime, timedelta
from jinja2 import Environment, DictLoader
import statistics

app = FastAPI()

# ------------------------------------------------------------------------------
# Database Connection Settings
# ------------------------------------------------------------------------------
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_DATABASE = os.getenv("DB_DATABASE", "SensorDB")
DB_USERNAME = os.getenv("DB_USERNAME", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Scam@1992")
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

# ------------------------------------------------------------------------------
# In-Memory Jinja2 Templates
# ------------------------------------------------------------------------------
templates_dict = {
    "layout.html": """
    <!DOCTYPE html>
    <html>
      <head>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" />
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
          body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          }
          h1, h2, h3, label {
            color: #ffcc00;
          }
          .card, .table {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
          }
          .table thead {
            background-color: #333;
          }
          .table thead th {
            color: #ffcc00;
          }
          .form-control, .btn {
            background-color: #333;
            border: 1px solid #444;
            color: #e0e0e0;
          }
          .btn:hover {
            background-color: #444;
          }
          .nav-link {
            color: #ffcc00 !important;
          }
          .nav-link:hover {
            color: #ffffff !important;
          }
          .summary-card {
            border: 1px solid #444;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            background-color: #1e1e1e;
          }
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
      // Data passed from server
      const timeLabels = {{ time_labels|safe }};
      const m1Temps = {{ m1_temps|safe }};
      const m2Temps = {{ m2_temps|safe }};
      const m1Press = {{ m1_press|safe }};
      const m2Press = {{ m2_press|safe }};
      
      // Temperature Chart
      const ctxTemp = document.getElementById('tempChart').getContext('2d');
      new Chart(ctxTemp, {
        type: 'line',
        data: {
          labels: timeLabels,
          datasets: [
            {
              label: 'Machine1 Temperature (°C)',
              data: m1Temps,
              borderColor: '#ffcc00',
              backgroundColor: 'rgba(255,204,0,0.1)',
              fill: true,
              tension: 0.2
            },
            {
              label: 'Machine2 Temperature (°C)',
              data: m2Temps,
              borderColor: '#00ccff',
              backgroundColor: 'rgba(0,204,255,0.1)',
              fill: true,
              tension: 0.2
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            x: {
              ticks: { color: '#e0e0e0' },
              grid: { color: '#444' }
            },
            y: {
              ticks: { color: '#e0e0e0' },
              grid: { color: '#444' }
            }
          },
          plugins: {
            legend: { labels: { color: '#ffcc00' } }
          }
        }
      });
      
      // Pressure Chart
      const ctxPress = document.getElementById('pressChart').getContext('2d');
      new Chart(ctxPress, {
        type: 'line',
        data: {
          labels: timeLabels,
          datasets: [
            {
              label: 'Machine1 Pressure (hPa)',
              data: m1Press,
              borderColor: '#ff6600',
              backgroundColor: 'rgba(255,102,0,0.1)',
              fill: true,
              tension: 0.2
            },
            {
              label: 'Machine2 Pressure (hPa)',
              data: m2Press,
              borderColor: '#66ff66',
              backgroundColor: 'rgba(102,255,102,0.1)',
              fill: true,
              tension: 0.2
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            x: {
              ticks: { color: '#e0e0e0' },
              grid: { color: '#444' }
            },
            y: {
              ticks: { color: '#e0e0e0' },
              grid: { color: '#444' }
            }
          },
          plugins: {
            legend: { labels: { color: '#ffcc00' } }
          }
        }
      });
    </script>
    {% endblock %}
    """,
}

env = Environment(loader=DictLoader(templates_dict))

def render_template(template_name: str, context: dict):
    template = env.get_template(template_name)
    return template.render(**context)

# ------------------------------------------------------------------------------
# Cyberpunk Dashboard Endpoint
# ------------------------------------------------------------------------------
@app.get("/cyberpunk", response_class=HTMLResponse)
def cyberpunk_dashboard(request: Request, start: str = None, end: str = None):
    """
    Displays a dashboard for both sensors:
      - Defaults to the last 24 hours if no range is provided.
      - Shows average, minimum, and maximum values for temperature and pressure for both Machine1 and Machine2.
      - Displays two graphs (temperature and pressure) with time series data.
    """
    # If no date range provided, default to last 24 hours.
    if not start or not end:
        query_m1 = """
            SELECT ID, MachineID, Timestamp, Temperature, Pressure
            FROM SensorData
            WHERE MachineID = 'Machine1'
              AND Timestamp >= DATEADD(HOUR, -24, GETDATE())
            ORDER BY Timestamp ASC
        """
        query_m2 = """
            SELECT ID, MachineID, Timestamp, Temperature, Pressure
            FROM SensorData
            WHERE MachineID = 'Machine2'
              AND Timestamp >= DATEADD(HOUR, -24, GETDATE())
            ORDER BY Timestamp ASC
        """
        start_val = ""
        end_val = ""
    else:
        start_dt = start.replace("T", " ")
        end_dt = end.replace("T", " ")
        query_m1 = f"""
            SELECT ID, MachineID, Timestamp, Temperature, Pressure
            FROM SensorData
            WHERE MachineID = 'Machine1'
              AND Timestamp BETWEEN '{start_dt}' AND '{end_dt}'
            ORDER BY Timestamp ASC
        """
        query_m2 = f"""
            SELECT ID, MachineID, Timestamp, Temperature, Pressure
            FROM SensorData
            WHERE MachineID = 'Machine2'
              AND Timestamp BETWEEN '{start_dt}' AND '{end_dt}'
            ORDER BY Timestamp ASC
        """
        start_val = start
        end_val = end

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get Machine1 data
        cursor.execute(query_m1)
        rows_m1 = cursor.fetchall()
        # Get Machine2 data
        cursor.execute(query_m2)
        rows_m2 = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert rows to list of dicts and extract chart data for each sensor.
        def process_rows(rows):
            data = []
            times = []
            temps = []
            press = []
            for r in rows:
                record = {
                    "ID": r[0],
                    "MachineID": r[1],
                    "Timestamp": str(r[2]),
                    "Temperature": float(r[3]),
                    "Pressure": float(r[4])
                }
                data.append(record)
                times.append(str(r[2]))
                temps.append(float(r[3]))
                press.append(float(r[4]))
            return data, times, temps, press

        m1_data, m1_times, m1_temps, m1_press = process_rows(rows_m1)
        m2_data, m2_times, m2_temps, m2_press = process_rows(rows_m2)
        
        # For chart labels, we can simply use the timestamps from Machine1 if available,
        # otherwise Machine2's. In a real app, you'd merge these carefully.
        time_labels = m1_times if m1_times else m2_times

        # Compute summary statistics for each sensor.
        def compute_stats(values):
            if values:
                avg = round(statistics.mean(values), 2)
                mn = round(min(values), 2)
                mx = round(max(values), 2)
                return avg, mn, mx
            return None, None, None

        m1_avg_temp, m1_min_temp, m1_max_temp = compute_stats(m1_temps)
        m1_avg_press, m1_min_press, m1_max_press = compute_stats(m1_press)
        m2_avg_temp, m2_min_temp, m2_max_temp = compute_stats(m2_temps)
        m2_avg_press, m2_min_press, m2_max_press = compute_stats(m2_press)

        html_content = render_template("cyberpunk.html", {
            "title": "Cyberpunk Dashboard",
            "start_value": start_val,
            "end_value": end_val,
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
        })
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>")
