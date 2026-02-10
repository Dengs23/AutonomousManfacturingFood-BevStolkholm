# dashboard_app.py - Web Dashboard Application
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from kafka_consumer import get_consumer
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'manufacturing-dashboard-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Kafka consumer
consumer = get_consumer()

# Store connected clients
connected_clients = set()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint for dashboard data"""
    data = consumer.get_latest_data()
    return jsonify(data)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'consumer_running': True,
        'topics': ['sensor-data', 'alerts', 'system-status', 'agent-events'],
        'timestamp': time.time()
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    connected_clients.add(request.sid)
    print(f"Client connected: {request.sid}")
    
    # Send initial data
    data = consumer.get_latest_data()
    emit('data_update', data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    connected_clients.discard(request.sid)
    print(f"Client disconnected: {request.sid}")

def background_kafka_updater():
    """Background thread to push Kafka updates to clients"""
    while True:
        time.sleep(2)  # Update every 2 seconds
        if connected_clients:
            data = consumer.get_latest_data()
            socketio.emit('data_update', data, room=list(connected_clients))

if __name__ == '__main__':
    # Start background updater thread
    updater_thread = threading.Thread(target=background_kafka_updater, daemon=True)
    updater_thread.start()
    
    # Start Flask app
    print("Starting Manufacturing Dashboard...")
    print("Dashboard available at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
