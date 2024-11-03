import chromadb
from pprint import pprint

from PIL import Image
from transformers import AutoProcessor, BlipForConditionalGeneration

import streamlit as st
import datetime
import random
import string
import pandas as pd


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


        for i in range(1, 6):
            filepath = f"VectorDB/data/{i}.jpeg"
            extracted_text = self.text_extractor.extract_text(filepath)
            metadatas = {"image_id": i, "image_path": filepath, "location": "Durham", "date": datetime.datetime.now().isoformat()}
            self.vector_db.store_feature_vector(filepath, extracted_text, metadatas=metadatas)

        # Query the database
        query = st.text_input("Enter your query")

        if query:
            results = self.vector_db.get_data(query, 3)
            st.write("Query Results:")
            # Prepare data for the table
            table_data = []

            # Prepare data for the table
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]

            # Create DataFrame with columns
            df = pd.DataFrame({
                "Text Encoding": documents,
                "Metadata": metadatas
            })

            csv_file_path = "VectorDB/data/results.csv"
            df.to_csv(csv_file_path, index=False)

            # Prepare HTML table with images
            table_html = """
            <table>
                <tr>
                    <th>Image</th>
                    <th>Text Encoding</th>
                    <th>Metadata</th>
                </tr>
            """
            for doc, meta in zip(documents, metadatas):
                image_path = meta.get("image_path", "")
                Image.open(image_path)
                
                meta_text = ""
                for key, value in meta.items():
                    meta_text += f"{key}: {value}  <br>"
                table_html += f"""
                <tr>
                    
                    <td><img src="{image_path}" width="100"></td>
                    <td>{doc}</td>
                    <td>{meta_text}</td>
                </tr>
                """
            table_html += "</table>"

            # Display the table with images
            st.html(table_html)


            # Allow users to download the CSV file
            with open(csv_file_path, "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f,
                    file_name="results.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    app = VectorDatabaseApp()
    app.run()