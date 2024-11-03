from PIL import Image
import io
from database.sightings import get_sighting

def display_image_from_sighting(sightingID):
    """
    Retrieve a sighting from MongoDB by its sightingID and display the stored image.
    
    Args:
        sightingID (str): The ID of the sighting to retrieve.
    """
    sighting = get_sighting(sightingID)
    if sighting and "image_data" in sighting:
        image_data = sighting["image_data"]  # Retrieve the binary image data
        image = Image.open(io.BytesIO(image_data))  # Convert binary data to an image
        image.show()  # Opens the image in the default image viewer
    else:
        print("No image data found for this sighting or sighting does not exist.")

# Example usage
# Replace 'your_sighting_id_here' with an actual sightingID from your database
display_image_from_sighting('a9943584-2ff6-4fc6-8bdc-4b2ea17030a5')
