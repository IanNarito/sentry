from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Base schema (shared properties)
class TargetBase(BaseModel):
    name: str = Field(..., description="Domain name or IP address", example="192.168.1.10")
    target_type: str = Field(..., pattern="^(domain|ip)$", description="Must be 'domain' or 'ip'")
    description: Optional[str] = None

# Schema for creating a target (input)
class TargetCreate(TargetBase):
    pass

# Schema for reading a target (output includes ID and timestamp)
class TargetResponse(TargetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True