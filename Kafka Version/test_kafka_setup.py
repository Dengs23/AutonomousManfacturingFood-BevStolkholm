#!/usr/bin/env python3
"""
Test script to verify Kafka dashboard setup
"""

import sys
import os

def check_files():
    print("📁 Checking required files...")
    required_files = [
        'kafka_config.py',
        'kafka_producer_enhanced.py',
        'kafka_consumer_enhanced.py',
        'dashboard_app_enhanced.py',
        'templates/dashboard_enhanced.html'
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            all_good = False
    
    return all_good

def check_python_modules():
    print("\n🐍 Checking Python modules...")
    modules = [
        ('flask', 'Flask'),
        ('flask_socketio', 'SocketIO'),
        ('kafka', 'KafkaProducer'),
        ('eventlet', 'eventlet')
    ]
    
    all_good = True
    for module, display_name in modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"   ✅ {display_name}")
        except ImportError:
            print(f"   ❌ {display_name} - Not installed")
            all_good = False
    
    return all_good

def print_instructions():
    print("\n" + "="*60)
    print("🚀 SWEDISH MANUFACTURING DASHBOARD SETUP")
    print("="*60)
    print("\n1️⃣  Install dependencies:")
    print("   pip install flask flask-socketio kafka-python eventlet")
    print("\n2️⃣  Test Kafka connection (optional):")
    print("   python kafka_producer_enhanced.py --interval 5")
    print("\n3️⃣  Start the dashboard:")
    print("   python dashboard_app_enhanced.py")
    print("\n4️⃣  Open browser:")
    print("   http://localhost:5000")
    print("\n5️⃣  If Kafka is not installed, dashboard will still work")
    print("   with simulated data.")
    print("="*60)

if __name__ == "__main__":
    print("🧪 Testing Kafka Dashboard Setup...")
    print("-" * 40)
    
    files_ok = check_files()
    modules_ok = check_python_modules()
    
    print("\n" + "-" * 40)
    if files_ok and modules_ok:
        print("✅ Setup looks good!")
        print_instructions()
    else:
        print("⚠️  Some issues found.")
        if not files_ok:
            print("   Run the commands from the previous chat to create missing files.")
        if not modules_ok:
            print("   Install missing modules: pip install flask flask-socketio kafka-python eventlet")
        print_instructions()
