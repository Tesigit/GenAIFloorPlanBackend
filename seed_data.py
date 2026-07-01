
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Example Plans (Few-Shot Data)
SEED_PLANS = [
    {
        "style": "modern",
        "metadata": {
            "bedrooms": 3,
            "bathrooms": 2,
            "description": "Efficient 3BHK with open kitchen"
        },
        "rooms": [
            {"label": "Living Room", "p1": {"x": 0, "y": 0}, "p2": {"x": 6, "y": 5}, "metadata": {"type": "living"}},
            {"label": "Kitchen", "p1": {"x": 6, "y": 0}, "p2": {"x": 10, "y": 4}, "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0, "y": 5}, "p2": {"x": 5, "y": 9}, "metadata": {"type": "bedroom"}},
            {"label": "Bedroom 2", "p1": {"x": 5, "y": 5}, "p2": {"x": 10, "y": 9}, "metadata": {"type": "bedroom"}},
            {"label": "Bedroom 3", "p1": {"x": 0, "y": 9}, "p2": {"x": 4, "y": 13}, "metadata": {"type": "bedroom"}},
            {"label": "Bathroom 1", "p1": {"x": 4, "y": 9}, "p2": {"x": 7, "y": 11}, "metadata": {"type": "bathroom"}},
            {"label": "Bathroom 2", "p1": {"x": 7, "y": 9}, "p2": {"x": 10, "y": 11}, "metadata": {"type": "bathroom"}},
        ]
    },
    {
        "style": "minimalist",
        "metadata": {
            "bedrooms": 2,
            "bathrooms": 1,
            "description": "Compact 2BHK minimalist layout"
        },
        "rooms": [
            {"label": "Living/Dining", "p1": {"x": 0, "y": 0}, "p2": {"x": 5, "y": 6}, "metadata": {"type": "living"}},
            {"label": "Kitchen", "p1": {"x": 5, "y": 0}, "p2": {"x": 8, "y": 3}, "metadata": {"type": "kitchen"}},
            {"label": "Bedroom 1", "p1": {"x": 0, "y": 6}, "p2": {"x": 4, "y": 9}, "metadata": {"type": "bedroom"}},
            {"label": "Bedroom 2", "p1": {"x": 4, "y": 6}, "p2": {"x": 8, "y": 9}, "metadata": {"type": "bedroom"}},
            {"label": "Bathroom", "p1": {"x": 5, "y": 3}, "p2": {"x": 8, "y": 5}, "metadata": {"type": "bathroom"}}
        ]
    }
]

def seed_db():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("Error: MONGODB_URI not found in .env")
        print("Please check your .env file.")
        return

    print(f"Connecting to MongoDB...")
    try:
        client = MongoClient(uri)
        # Force a connection check
        client.admin.command('ping')
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    db = client.get_default_database()
    
    collection = db["seed_plans"]
    
    # Optional: Clear existing seeds to avoid duplicates
    # collection.delete_many({}) 
    
    print(f"Inserting {len(SEED_PLANS)} seed plans...")
    try:
        result = collection.insert_many(SEED_PLANS)
        print(f"Success! Inserted IDs: {result.inserted_ids}")
    except Exception as e:
        print(f"Insert failed: {e}")

if __name__ == "__main__":
    seed_db()

