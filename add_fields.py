"""Script to add phone_number and address fields to existing products"""
import random
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Indian phone numbers (10 digits, starting with 6-9)
def generate_indian_phone():
    """Generate random Indian phone number"""
    first_digit = random.choice(['6', '7', '8', '9'])
    remaining = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f"+91 {first_digit}{remaining[:4]} {remaining[4:]}"

# Indian addresses
INDIAN_CITIES = [
    "Mumbai, Maharashtra",
    "Delhi, Delhi",
    "Bangalore, Karnataka",
    "Hyderabad, Telangana",
    "Chennai, Tamil Nadu",
    "Kolkata, West Bengal",
    "Pune, Maharashtra",
    "Ahmedabad, Gujarat",
    "Jaipur, Rajasthan",
    "Surat, Gujarat",
    "Lucknow, Uttar Pradesh",
    "Kanpur, Uttar Pradesh",
    "Nagpur, Maharashtra",
    "Indore, Madhya Pradesh",
    "Thane, Maharashtra",
    "Bhopal, Madhya Pradesh",
    "Visakhapatnam, Andhra Pradesh",
    "Vadodara, Gujarat",
    "Ghaziabad, Uttar Pradesh",
    "Ludhiana, Punjab",
    "Agra, Uttar Pradesh",
    "Nashik, Maharashtra",
    "Faridabad, Haryana",
    "Meerut, Uttar Pradesh",
    "Rajkot, Gujarat",
    "Varanasi, Uttar Pradesh",
    "Srinagar, Jammu and Kashmir",
    "Amritsar, Punjab",
    "Chandigarh, Punjab",
    "Coimbatore, Tamil Nadu"
]

STREET_TYPES = [
    "MG Road", "Station Road", "Main Street", "Park Avenue", "Gandhi Nagar",
    "Nehru Place", "Sector", "Industrial Area", "Market Road", "Ring Road",
    "Civil Lines", "Cantonment", "Old City", "New Colony", "Shopping Complex"
]

def generate_indian_address():
    """Generate random Indian address"""
    building_no = random.randint(1, 999)
    street = random.choice(STREET_TYPES)
    city = random.choice(INDIAN_CITIES)
    pincode = random.randint(100000, 999999)
    
    return f"{building_no}, {street}, {city} - {pincode}"

def main():
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_database = os.getenv("MONGODB_DATABASE", "product")
    mongodb_collection = os.getenv("MONGODB_COLLECTION", "products")
    
    if not mongodb_uri:
        print("❌ Error: MONGODB_URI not found in .env file")
        return
    
    client = MongoClient(mongodb_uri)
    db = client[mongodb_database]
    collection = db[mongodb_collection]
    
    # Get all products
    print("Fetching products...")
    products = list(collection.find())
    total = len(products)
    print(f"Found {total} products")
    
    if total == 0:
        print("❌ No products found in database")
        return
    
    # Update each product with new fields
    print("\nAdding phone_number and address fields...")
    updated_count = 0
    
    for i, product in enumerate(products, 1):
        phone_number = generate_indian_phone()
        address = generate_indian_address()
        
        # Update the product
        result = collection.update_one(
            {"_id": product["_id"]},
            {
                "$set": {
                    "phone_number": phone_number,
                    "address": address
                }
            }
        )
        
        if result.modified_count > 0:
            updated_count += 1
        
        # Progress indicator
        if i % 50 == 0 or i == total:
            print(f"  Progress: {i}/{total} ({(i/total)*100:.1f}%)")
    
    print(f"\n✅ Successfully updated {updated_count} products!")
    print(f"   Added fields: phone_number, address")
    
    # Show sample
    print("\n📋 Sample product:")
    sample = collection.find_one()
    print(f"   Title: {sample.get('title', 'N/A')}")
    print(f"   Phone: {sample.get('phone_number', 'N/A')}")
    print(f"   Address: {sample.get('address', 'N/A')}")
    
    client.close()
    print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()
