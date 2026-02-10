from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import threading
import time
import random
from datetime import datetime

app = Flask(__name__)
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
        
        return {
            "cycle_id": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "factory": factory,
            "sensor_data": {
                "temperature_c": round(22.0 + random.uniform(-2, 4), 1),
                "pressure_bar": round(1.01 + random.uniform(-0.05, 0.05), 3),
                "ph_level": round(random.uniform(6.5, 7.5), 2),
                "vibration_x": round(random.uniform(0.1, 0.8), 3),
                "flow_rate_lph": round(random.uniform(1000, 3000), 0)
            },
            "alerts": [],
            "system_metrics": {
                "uptime": round(99.5 + random.uniform(-0.5, 0.5), 1),
                "efficiency": round(96.0 + random.uniform(-2, 2), 1),
                "quality": round(98.0 + random.uniform(-1, 1), 1)
            }
        }

simulator = SwedishManufacturingSimulator()

@app.route('/')
def index():
    return render_template('dashboard_working.html')

@app.route('/api/data')
def get_data():
    return jsonify(simulator.generate_data())

if __name__ == '__main__':
    print("Swedish Manufacturing Dashboard: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
