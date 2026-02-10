from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from kafka_consumer_enhanced import get_realtime_consumer
import threading
import time
import json
from datetime import datetime
import pandas as pd

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'swedish-manufacturing-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize Kafka consumer
consumer = None
connected_clients = set()
dashboard_stats = {
    'start_time': datetime.now(),
    'total_updates': 0,
    'total_clients': 0
}

def initialize_consumer():
    global consumer
    try:
        consumer = get_realtime_consumer()
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
            return jsonify({'error': str(e), 'status': 'offline'}), 500
    else:
        return jsonify({
            'status': 'offline',
            'message': 'Kafka not connected',
            'sensor_data': {},
            'alerts': [],
            'system_status': None,
            'agent_status': []
        })

@app.route('/api/trends/<metric>')
def get_trends(metric):
    if consumer:
        try:
            trend_data = consumer.get_time_series_data(metric, 20)
            return jsonify(trend_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'timestamps': [], 'values': []})

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'dashboard_stats': dashboard_stats,
        'connected_clients': len(connected_clients),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trigger-cycle', methods=['POST'])
def trigger_cycle():
    # In production, this would trigger an actual manufacturing cycle
    return jsonify({
        'status': 'success', 
        'message': 'Swedish manufacturing cycle triggered',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/reset', methods=['POST'])
def reset_system():
    return jsonify({
        'status': 'success', 
        'message': 'Swedish manufacturing system reset',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('connect')
def handle_connect():
    connected_clients.add(request.sid)
    dashboard_stats['total_clients'] += 1
    print(f"✅ Client connected: {request.sid}")
    
    # Send initial data
    if consumer:
        try:
            data = consumer.get_latest_data()
            emit('initial_data', data, room=request.sid)
        except Exception as e:
            emit('error', {'message': str(e)}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    connected_clients.discard(request.sid)
    print(f"❌ Client disconnected: {request.sid}")

@socketio.on('request_update')
def handle_update_request():
    if consumer and request.sid in connected_clients:
        try:
            data = consumer.get_latest_data()
            emit('data_update', data, room=request.sid)
        except Exception as e:
            emit('error', {'message': str(e)}, room=request.sid)

def background_kafka_updater():
    """Real-time background updates (every 1 second)"""
    while True:
        time.sleep(1)  # Update every second
        if connected_clients and consumer:
            try:
                data = consumer.get_latest_data()
                dashboard_stats['total_updates'] += 1
                
                # Send full update to all clients
                socketio.emit('data_update', data, room=list(connected_clients))
                
                # Send alert notifications if new alerts
                if data.get('alerts') and len(data['alerts']) > 0:
                    socketio.emit('alert_notification', {
                        'count': len(data['alerts']),
                        'latest': data['alerts'][0] if data['alerts'] else None,
                        'timestamp': datetime.now().isoformat()
                    }, room=list(connected_clients))
                
            except Exception as e:
                print(f"⚠️ Update error: {e}")

if __name__ == '__main__':
    # Create required directories
    import os
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Initialize Kafka consumer
    initialize_consumer()
    
    # Start background updater
    updater_thread = threading.Thread(target=background_kafka_updater, daemon=True)
    updater_thread.start()
    
    # Print startup message
    print("\n" + "="*60)
    print("🏭 SWEDISH MANUFACTURING DASHBOARD")
    print("="*60)
    print("🌐 Dashboard URL: http://localhost:5000")
    print("📡 Kafka Topics: manufacturing-sensor-data, manufacturing-alerts")
    print("🔄 Real-time updates: Every 1 second")
    print("🇸🇪 Region: Stockholm, Sweden")
    print("="*60 + "\n")
    
    # Start Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
