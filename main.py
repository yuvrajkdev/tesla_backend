from fastapi import FastAPI, HTTPException
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError
from models import TeamMember, TeamMemberInDB
from database import team_members_collection
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/items/{item_id}")
async def read_item(item_id : int):
    return {"item_id": item_id}

# Helper function to convert BSON to JSON-friendly format
def bson_to_json(TeamMember):
    TeamMember["_id"] = str(TeamMember["_id"])  # Convert ObjectId to string
    return TeamMember

@app.post("/teammember/", response_model=TeamMemberInDB)
async def create_teammember(team_member: TeamMember):
    """Create a new TeamMember."""
    teammember_data = team_member.model_dump()  # Convert instance to dict
    
    # Check if a document with the same 'id' exists in the database
    existing_member = await team_members_collection.find_one({"id": teammember_data["id"]})
    
    if existing_member:
        # If a member with the same 'id' exists, raise an error
        raise HTTPException(status_code=400, detail="TeamMember with this ID already exists")
    
    try:
        # Insert the team member into the collection
        result = await team_members_collection.insert_one(teammember_data)
        
        # After insertion, add the inserted _id to the data
        teammember_data["_id"] = str(result.inserted_id)
        
        # Return TeamMemberInDB
        return TeamMemberInDB(_id=teammember_data["_id"], **team_member.model_dump())
        
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="TeamMember with this email already exists")

    
@app.get("/teammembers/", response_model=list[TeamMemberInDB])
async def get_all_teammembers():
    """Get all users."""
    users_cursor = team_members_collection.find()  # This returns a cursor
    users = await users_cursor.to_list(length=None)  # Convert to a list
    return [bson_to_json(user) for user in users]

@app.get("/teammember/{teammember_id}", response_model=TeamMemberInDB)
async def get_teammember(teammember_id: str):
    """Get a TeamMember by ID."""
    try:
        TeamMember = await team_members_collection.find_one({"_id": ObjectId(teammember_id)})
        if not TeamMember:
            raise HTTPException(status_code=404, detail="TeamMember not found")
        return bson_to_json(TeamMember)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid TeamMember ID format")

@app.put("/teammembers/{teammember_id}", response_model=TeamMemberInDB)
async def update_teammember(teammember_id: str, TeamMember: TeamMember):
    """Update a TeamMember's details."""
    try:
        result = await team_members_collection.update_one(
            {"_id": ObjectId(teammember_id)}, {"$set": TeamMember.model_dump()}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="TeamMember not found")
        updated_TeamMember = await team_members_collection.find_one({"_id": ObjectId(teammember_id)})
        return bson_to_json(updated_TeamMember)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid TeamMember ID format")

@app.delete("/teammembers/{teammember_id}")
async def delete_teammember(teammember_id: str):
    """Delete a TeamMember."""
    try:
        result = await team_members_collection.delete_one({"_id": ObjectId(teammember_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="TeamMember not found")
        return {"message": "TeamMember deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid TeamMember ID format")