# app.py
from flask import Flask, render_template, jsonify
from neca.events import event, fire_global
import threading
import time

app = Flask(__name__)

# Dashboard data (simulated for this example)
dashboard_data = {
    "sports": "No updates yet.",
    "weather": "No updates yet.",
    "alerts": "No alerts."
}

# Event to update sports data
@event("update_sports")
def update_sports_handler(context, data):
    dashboard_data["sports"] = data
    print(f"Sports Update: {data}")

# Event to update weather data
@event("update_weather")
def update_weather_handler(context, data):
    dashboard_data["weather"] = data
    print(f"Weather Update: {data}")

# Event to update alerts
@event("update_alerts")
def update_alerts_handler(context, data):
    dashboard_data["alerts"] = data
    print(f"Alert Update: {data}")

# Route to serve the dashboard page
@app.route("/")
def index():
    return render_template("index.html")

# Route to get the latest dashboard data
@app.route("/data")
def get_data():
    return jsonify(dashboard_data)

# Background function to simulate event firing
# def simulate_events():
#     time.sleep(2)
#     fire_global(event_name="update_sports", data="Live game score: 2-1", delay=1)
#     fire_global(event_name="update_weather", data="Clear skies with a chance of rain", delay=3)
#     fire_global(event_name="update_alerts", data="Security alert in your area", delay=5)

if __name__ == "__main__":
    # Start the event simulation in a separate thread
    # threading.Thread(target=simulate_events).start()
    app.run(debug=True,port=5003)