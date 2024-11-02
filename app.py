from flask import Flask, render_template, request, jsonify
import json
import os
import sys

# Add the classifiers directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'NN'))

# Now you can import AnimalClassifier
from animalClassifier import AnimalClassifier

app = Flask(__name__, template_folder="Map/Templates")
app.config.from_pyfile('config.py')

travelled_locations = []

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=app.config['MAPBOX_ACCESS_TOKEN'])

@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.get_json()
    if data not in travelled_locations:
        travelled_locations.append(data)
        with open('locations.json', 'w') as f:
            json.dump(travelled_locations, f)
    return jsonify(success=True)

@app.route('/get_locations', methods=['GET'])
def get_locations():
    try:
        with open('locations.json', 'r') as f:
            locations = json.load(f)
        return jsonify(locations)
    except Exception as e:
        print(f"Error reading locations.json: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/get_grid', methods=['GET'])
def get_grid():
    min_lat = float(request.args.get('min_lat', -90))
    max_lat = float(request.args.get('max_lat', 90))
    min_lon = float(request.args.get('min_lon', -180))
    max_lon = float(request.args.get('max_lon', 180))
    grid_size = float(request.args.get('grid_size', 10))
    
    grid = generate_grid(min_lat, max_lat, min_lon, max_lon, grid_size)
    return jsonify(grid)

@app.route('/classify_image', methods=['POST'])
def classify_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save temp file
        temp_file_path = 'temp.jpg'
        file.save(temp_file_path)

        # Classify the image
        classifier = AnimalClassifier()
        animal, species = classifier.classify(temp_file_path)
       
        # Optionally, delete the temporary file after processing
        os.remove(temp_file_path)
        

        return jsonify({"animal": animal, "species": species})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_grid(min_lat, max_lat, min_lon, max_lon, grid_size):
    grid = {
        "type": "FeatureCollection",
        "features": []
    }

    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            grid["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lon, lat],
                        [lon + grid_size, lat],
                        [lon + grid_size, lat + grid_size],
                        [lon, lat + grid_size],
                        [lon, lat]
                    ]]
                },
                "properties": {
                    "explored": False
                }
            })
            lon += grid_size
        lat += grid_size

    return grid

if __name__ == '__main__':
    print(AnimalClassifier().classify("NN/monarch.jpg"))
    app.run(debug=True)