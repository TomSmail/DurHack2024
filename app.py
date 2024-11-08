from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import sys
import base64
from PIL import Image
import io
import uuid
import math
from datetime import datetime
from torchvision import transforms

# Add the classifiers directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'NN'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

from NN.animalClassifier import AnimalClassifier
from database.mongodb_connection import db  # Import the MongoDB database instance

# Access the sightings collection from the imported MongoDB connection
sightings_collection = db["sightings"]

app = Flask(__name__, template_folder="Map/Templates")
app.config.from_pyfile('config.py')

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=app.config['MAPBOX_ACCESS_TOKEN'])

@app.route('/camera')
def camera():
    return render_template('camera.html', page='camera')

@app.route('/animals')
def animals():
    return render_template('animalList.html', page='animals')

@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.get_json()
    travelled_locations = []

    try:
        with open('locations.json', 'r') as f:
            travelled_locations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if data not in travelled_locations:
        travelled_locations.append(data)
        with open('locations.json', 'w') as f:
            json.dump(travelled_locations, f)

    return jsonify(success=True)

@app.route('/classify_image', methods=['POST'])
def classify_image():
    data = request.get_json()

    if 'image' not in data:
        return jsonify({"error": "No image data"}), 400

    base64_image = data['image']
    latitude = data.get('latitude', 0.0)
    longitude = data.get('longitude', 0.0)

    try:
        # Decode the base64 image
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data))

        if image.mode == 'RGBA':
            image = image.convert('RGB')

        # Convert the image to binary data for MongoDB
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_binary = image_bytes.getvalue()

        # Classify the image
        classifier = AnimalClassifier()
        animal, species = classifier.classify(io.BytesIO(image_binary))

        # Save sighting information with binary image data
        sighting_id = str(uuid.uuid4())
        sighting_data = {
            "sightingID": sighting_id,
            "image_data": image_binary,
            "time": datetime.utcnow(),
            "geolocation": {'latitude': latitude, 'longitude': longitude},
            "ai_identification": {'animal': animal, 'species': species},
            "user_identification": None
        }
        sightings_collection.insert_one(sighting_data)

        return jsonify({"animal": animal, "species": species, "sightingID": sighting_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_grid', methods=['GET'])
def get_grid():
    min_lat = float(request.args.get('min_lat'))
    max_lat = float(request.args.get('max_lat'))
    min_lon = float(request.args.get('min_lon'))
    max_lon = float(request.args.get('max_lon'))
    grid_size = float(request.args.get('grid_size', 0.001))

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

@app.route('/get_image/<sightingID>')
def get_image(sightingID):
    sighting = sightings_collection.find_one({"sightingID": sightingID})
    if sighting and "image_data" in sighting:
        image_data = sighting["image_data"]
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
    return "Image not found", 404

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

if __name__ == '__main__':
    app.run(debug=True)