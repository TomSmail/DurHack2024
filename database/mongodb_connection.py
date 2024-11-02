from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connection URI
mongo_uri = os.getenv("MONGO_URI")

# Set up MongoClient with extended timeout settings
client = MongoClient(mongo_uri, socketTimeoutMS=60000, connectTimeoutMS=60000)
db = client['Durhack2024']

print("Connected to MongoDB!")