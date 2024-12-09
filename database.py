from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection settings
MONGO_URI = "mongodb://localhost:27017"  # Replace with your URI
DATABASE_NAME = "tesla_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# Export the collection to use it in your routes
team_members_collection = db["team_members"]