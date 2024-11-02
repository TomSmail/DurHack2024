import chromadb
from pprint import pprint

from PIL import Image
from transformers import AutoProcessor, BlipForConditionalGeneration

client = chromadb.Client()

collection = client.create_collection("images")

class TextExtractor():
    def __init__(self):
        # Model cuts off the last layer of the ResNet50 model to create a feature extractor
        self.processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    
    def extract_text(self, image_path):
        image = Image.open(image_path)
        text = "A picture of"
        inputs = self.processor(images=image, text=text, return_tensors="pt")

        outputs = self.model.generate(**inputs)
        return self.processor.decode(outputs[0], skip_special_tokens=True)
    


def store_feature_vector(image_id, document, metadatas=None):
    # Store the feature vector in ChromaDB
    collection.add(
        ids=image_id,
        documents=[document],
        metadatas=metadatas
    )

def get_data(query):
    return collection.query(
        query_texts=[query],
        n_results=1,
    )

if __name__ == '__main__':
    text_extractor = TextExtractor()
    image_path = 'NN/monarch.jpg'
    document = text_extractor.extract_text(image_path)
    print(f"DOCUMENT: {document}")
    store_feature_vector('monarch', document, metadatas={'date': '2024-10-02', 'location': 'Durham', 'species': 'Butterfly', 'subspecies': 'Monarch'})
    pprint(collection.get('monarch'))

    # Query the collection
    query = 'Please get me all the images of butterflies'
    result = get_data(query)
    pprint(result)