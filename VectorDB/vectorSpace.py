import chromadb
from pprint import pprint

from PIL import Image
from transformers import AutoProcessor, BlipForConditionalGeneration

import streamlit as st
import time

import random
import string


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
    

class VectorDatabase():
    def __init__(self):
        self.client = chromadb.Client()
        self.collection_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        if self.collection_name in self.client.list_collections():
            print(f"Collection {self.collection_name} already exists")
            self.collection = self.client.get_collection(self.collection_name)
        else:
            print(f"Creating collection {self.collection_name}")
            self.collection = self.client.create_collection(self.collection_name)
    
    def store_feature_vector(self, image_id, document, metadatas=None):
        # Store the feature vector in ChromaDB
        self.collection.add(
            ids=image_id,
            documents=[document],
            metadatas=metadatas
        )
    
    def get_data(self, query, n=1):
        return self.collection.query(
            query_texts=[query],
            n_results=n,
        )


class VectorDatabaseApp:
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.vector_db = VectorDatabase()

    def run(self):
        st.title("Vector Database Query with LLM")

        # Upload image
        # uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

        for i in range(1, 6):
            filepath = f"VectorDB/data/{i}.jpeg"
            extracted_text = self.text_extractor.extract_text(filepath)
            self.vector_db.store_feature_vector(filepath, extracted_text, metadatas={"image_id": i})

        # if uploaded_file is not None:
        #     # Extract text from the image
        #     image_path = uploaded_file.name
        #     with open(image_path, "wb") as f:
        #         f.write(uploaded_file.getbuffer())

        #     extracted_text = self.text_extractor.extract_text(image_path)
        #     st.write(f"Extracted Text: {extracted_text}")
        #     # Store feature vector in the database
        #     image_id = image_path
        #     document = extracted_text
        #     st.write(f"Storing feature vector for image {image_path}")

        #     self.vector_db.store_feature_vector(image_id, document)


        # Query the database
        query = st.text_input("Enter your query")

        if query:
            results = self.vector_db.get_data(query, 3)
            st.write("Query Results:")
            # Prepare data for the table
            table_data = []
            for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                
                table_data.append({"Document": doc, "Metadata": meta})
                

            # Display the table
            st.table(table_data)

if __name__ == "__main__":
    app = VectorDatabaseApp()
    app.run()