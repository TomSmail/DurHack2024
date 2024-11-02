from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)
travelled_locations = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.get_json()
    travelled_locations.append(data)
    with open('locations.json', 'w') as f:
        json.dump(travelled_locations, f)
    return jsonify(success=True)

@app.route('/get_locations', methods=['GET'])
def get_locations():
    with open('locations.json', 'r') as f:
        locations = json.load(f)
    return jsonify(locations)


if __name__ == '__main__':
    app.run(debug=True)
