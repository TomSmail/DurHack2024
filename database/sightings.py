# sightings.py
from database.mongodb_connection import db
from datetime import datetime

sightings_collection = db['sightings']

def create_sighting(sightingID, imgurl, time, geolocation, ai_identification, user_identification):
    new_sighting = {
        "sightingID": sightingID,
        "imgurl": imgurl,
        "time": time,
        "geolocation": geolocation,
        "ai_identification": ai_identification,
        "user_identification": user_identification
    }
    sightings_collection.insert_one(new_sighting)
    print(f"Sighting {sightingID} added!")

def get_sighting(sightingID):
    sighting = sightings_collection.find_one({"sightingID": sightingID})
    print("Retrieved sighting:", sighting)
    return sighting

def update_sighting_identification(sightingID, ai_identification=None, user_identification=None):
    update_fields = {}
    if ai_identification:
        update_fields["ai_identification"] = ai_identification
    if user_identification:
        update_fields["user_identification"] = user_identification

    sightings_collection.update_one(
        {"sightingID": sightingID},
        {"$set": update_fields}
    )
    print(f"Sighting {sightingID} updated!")

def delete_sighting(sightingID):
    sightings_collection.delete_one({"sightingID": sightingID})
    print(f"Sighting {sightingID} deleted!")