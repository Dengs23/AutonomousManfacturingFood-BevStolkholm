from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from kafka_consumer_fixed import get_consumer
import threading
import time
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'manufacturing-dashboard-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

consumer = None
connected_clients = set()

def initialize_consumer():
    global consumer
    try:
        consumer = get_consumer()
        print("✅ Swedish Manufacturing Consumer Initialized")
    except Exception as e:
        print(f"❌ Kafka Error: {e}")
        consumer = None

@app.route('/')
def index():
    return render_template('dashboard_enhanced.html')

@app.route('/api/data')
def get_data():
    if consumer:
        try:
            data = consumer.get_latest_data()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({
            'sensor_data': {},
            'alerts': [],
            'system_status': None,
            'agent_status': []
        })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'kafka_connected': consumer is not None,
        'timestamp': time.time()
    })

@socketio.on('connect')
def handle_connect():
    connected_clients.add(request.sid)
    print(f"✅ Client connected: {request.sid}")
    
    if consumer:
        try:
            data = consumer.get_latest_data()
            socketio.emit('data_update', data, room=request.sid)
        except Exception as e:
            print(f"Error sending initial data: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    connected_clients.discard(request.sid)
    print(f"❌ Client disconnected: {request.sid}")

def background_kafka_updater():
    while True:
        time.sleep(1)
        if connected_clients and consumer:
            try:
                data = consumer.get_latest_data()
                socketio.emit('data_update', data, room=list(connected_clients))
            except Exception as e:
                print(f"Update error: {e}")

if __name__ == '__main__':
    initialize_consumer()
    
    import os
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    updater_thread = threading.Thread(target=background_kafka_updater, daemon=True)
    updater_thread.start()
    
    print("\n" + "="*60)
    print("🏭 SWEDISH MANUFACTURING DASHBOARD")
    print("="*60)
    print("🌐 Dashboard: http://localhost:5000")
    print("🔄 Real-time updates: Every 1 second")
    print("🇸🇪 Region: Stockholm, Sweden")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
