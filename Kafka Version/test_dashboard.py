from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    return jsonify({
        'status': 'success',
        'message': 'Dashboard API is working',
        'sensors': {'temperature': 25.5, 'pressure': 1.0},
        'alerts': []
    })

if __name__ == '__main__':
    print("Starting dashboard...")
    print("Open: http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
