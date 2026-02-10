from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import threading
import time
import random
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
socketio = SocketIO(app, cors_allowed_origins="*")

# Swedish manufacturing simulator
class SwedishManufacturingSimulator:
    def __init__(self):
        self.cycle_count = 0
        self.factories = [
            "Stockholm Brewery AB",
            "Malmo Food Processing",
            "Gothenburg Beverage Inc",
            "Uppsala Dairy Plant"
        ]
    
    def generate_data(self):
        self.cycle_count += 1
        factory = random.choice(self.factories)
        
        # Generate sensor readings
        temp = round(22.0 + random.uniform(-2, 4), 1)
        vibration = round(random.uniform(0.1, 0.8), 3)
        
        # Check for alerts
        alerts = []
        if temp > 26:
            alerts.append({
                "message": f"High temperature: {temp}°C",
                "severity": "medium",
                "timestamp": datetime.now().isoformat()
            })
        
        if vibration > 0.6:
            alerts.append({
                "message": f"High vibration: {vibration}",
                "severity": "high",
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "cycle_id": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "factory": factory,
            "sensor_data": {
                "temperature_c": temp,
                "pressure_bar": round(1.01 + random.uniform(-0.05, 0.05), 3),
                "ph_level": round(random.uniform(6.5, 7.5), 2),
                "vibration_x": vibration,
                "vibration_y": round(random.uniform(0.1, 0.8), 3),
                "flow_rate_lph": round(random.uniform(1000, 3000), 0),
                "co2_ppm": round(random.uniform(400, 800), 0),
                "brix_level": round(random.uniform(10, 20), 1),
                "energy_kwh": round(random.uniform(500, 1500), 0)
            },
            "alerts": alerts,
            "system_metrics": {
                "uptime": round(99.5 + random.uniform(-0.5, 0.5), 1),
                "efficiency": round(96.0 + random.uniform(-2, 2), 1),
                "quality": round(98.0 + random.uniform(-1, 1), 1)
            }
        }

simulator = SwedishManufacturingSimulator()
connected_clients = set()

@app.route('/')
def index():
    return render_template('dashboard_enhanced.html')

@app.route('/api/data')
def get_data():
    return jsonify(simulator.generate_data())

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cycles": simulator.cycle_count
    })

@socketio.on('connect')
def handle_connect():
    connected_clients.add(request.sid)
    print(f"✅ Client connected: {request.sid}")
    
    # Send initial data
    data = simulator.generate_data()
    socketio.emit('data_update', data, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    connected_clients.discard(request.sid)
    print(f"❌ Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_update_request():
    if request.sid in connected_clients:
        data = simulator.generate_data()
        socketio.emit('data_update', data, room=request.sid)

def background_updater():
    """Send updates to all connected clients every 2 seconds"""
    while True:
        time.sleep(2)
        if connected_clients:
            data = simulator.generate_data()
            socketio.emit('data_update', data, room=list(connected_clients))

if __name__ == '__main__':
    # Start background updater
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    print("\n" + "="*60)
    print("🏭 SWEDISH MANUFACTURING DASHBOARD")
    print("="*60)
    print("🌐 Dashboard: http://localhost:5000")
    print("🔄 Real-time updates: Every 2 seconds")
    print("🇸🇪 Region: Stockholm, Sweden")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
