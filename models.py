from pydantic import BaseModel
from typing import Optional

# Schema for incoming requests
class TeamMember(BaseModel):
    id: int
    name: str
    role: str
    photo: Optional[str] = None

# Schema for database objects
class TeamMemberInDB(TeamMember):
    _id: str