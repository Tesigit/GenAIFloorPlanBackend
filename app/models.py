from __future__ import annotations
from typing import List, Literal, Tuple, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class Point(BaseModel):
    x: float
    y: float

class Room(BaseModel):
    label: str
    p1: Point  # top-left
    p2: Point  # bottom-right
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("p2")
    @classmethod
    def validate_coords(cls, v: Point, info):
        """Auto-swap p1/p2 if coordinates are reversed — never raise an error."""
        if not info.data or 'p1' not in info.data:
            return v
        p1 = info.data['p1']
        if not isinstance(p1, Point):
            return v
        # Auto-fix swapped coordinates instead of raising
        fixed_x = max(v.x, p1.x + 0.1) if v.x <= p1.x else v.x
        fixed_y = max(v.y, p1.y + 0.1) if v.y <= p1.y else v.y
        if fixed_x != v.x or fixed_y != v.y:
            return Point(x=fixed_x, y=fixed_y)
        return v

class Floor(BaseModel):
    name: str  # "Ground Floor", "First Floor", etc.
    rooms: List[Room]

class Plan(BaseModel):
    units: Literal["meters", "feet"] = Field(default="meters")
    rooms: Optional[List[Room]] = None
    floors: Optional[List[Floor]] = None

class FloorConfig(BaseModel):
    name: str = "Floor"
    bedrooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    livingRooms: int = 0
    balconies: int = 0
    parking: bool = False
    hasLift: bool = False

class Constraints(BaseModel):
    length: float   # vertical depth of plot
    width: float    # horizontal width of plot
    floors: int = 1 # number of floors
    floorDetails: List[FloorConfig] = Field(default_factory=list)
    bedrooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    livingRooms: int = 0
    balconies: int = 0
    specialRequirements: List[str] = []
    stylePreference: str = "modern"
    prompt: str = ""

class GenerateResult(BaseModel):
    plan: Plan
    iterations: int
    messages: List[str] = []
    valid: bool
    prompt_sent: str = ""
    source: str = "ai"        # "ai" or "fallback"

class ValidationIssue(BaseModel):
    code: str
    message: str
    room_indices: Optional[List[int]] = None

class ValidationResult(BaseModel):
    valid: bool
    issues: List[ValidationIssue] = []
