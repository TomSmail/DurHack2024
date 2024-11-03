from flask import Flask, render_template, request, jsonify
import json
import os
import sys
import base64
from PIL import Image
import io
import math

from torchvision import transforms

# Add the classifiers directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'NN'))

# Now you can import AnimalClassifier
from NN.animalClassifier import AnimalClassifier
from database.sightings import create_sighting

app = Flask(__name__, template_folder="Map/Templates")
app.config.from_pyfile('config.py')

travelled_locations = []

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=app.config['MAPBOX_ACCESS_TOKEN'], page='map')

@app.route('/camera')
def camera():
    return render_template('camera.html', page='camera')

@app.route('/animals')
def animals():
    return render_template('animals.html', page='animals')

@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.get_json()

    try:
        with open('locations.json', 'r') as f:
            travelled_locations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        travelled_locations = []

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
    min_lat = float(request.args.get('min_lat'))
    max_lat = float(request.args.get('max_lat'))
    min_lon = float(request.args.get('min_lon'))
    max_lon = float(request.args.get('max_lon'))
    grid_size = float(request.args.get('grid_size', 0.001))  # Grid size in degrees
    
    grid = generate_grid(min_lat, max_lat, min_lon, max_lon, grid_size)
    
    # Load explored locations
    try:
        with open('locations.json', 'r') as f:
            explored_locations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        explored_locations = []
    
    # Mark explored cells
    for feature in grid['features']:
        coords = feature['geometry']['coordinates'][0]
        min_lon, min_lat = coords[0]
        max_lon, max_lat = coords[2]
        
        for location in explored_locations:
            if min_lat <= location['lat'] <= max_lat and min_lon <= location['lon'] <= max_lon:
                feature['properties']['explored'] = True
                break
    
    return jsonify(grid)

@app.route('/classify_image', methods=['POST'])
def classify_image():
    
    data = request.get_json()
    if 'image' not in data:
        return jsonify({"error": "No image data"}), 400

    base64_image = data['image']

    try:

        # Decode the base64 image
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))

        if image.mode == 'RGBA':
            image = image.convert('RGB')

        # Save temp file
        temp_file_path = 'temp.jpg'
        image.save(temp_file_path)

        # Classify the image
        classifier = AnimalClassifier()
        animal, species = classifier.classify(temp_file_path)

        create_sighting(
            sightingID=sighting_id,
            imgurl=image_path,
            time=datetime.now(),
            geolocation={'latitude': latitude, 'longitude': longitude},
            ai_identification={'animal': animal, 'species': species},
            user_identification=None
        )
       
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
        lon_diff = grid_size / math.cos(math.radians(lat))
        while lon < max_lon:
            grid["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [lon, lat],
                        [lon + lon_diff, lat],
                        [lon + lon_diff, lat + grid_size],
                        [lon, lat + grid_size],
                        [lon, lat]
                    ]]
                },
                "properties": {
                    "explored": False
                }
            })
            lon += lon_diff
        lat += grid_size

    return grid

def get_explored_grids_count(grid_data):
    explored_count = 0
    for feature in grid_data['features']:
        if feature['properties'].get('explored', False):
            explored_count += 1
    return explored_count

if __name__ == '__main__':
    app.run(debug=True)