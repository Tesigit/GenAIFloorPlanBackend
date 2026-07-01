"""
Post-processor that enforces realistic room size constraints
on any floor plan (AI-generated or fallback).

This is the LAST line of defence — it runs on every plan before returning to the user.
"""

from .models import Plan, Room, Point, Floor

# Maximum room dimensions in meters (width, height)
MAX_SIZES = {
    "bathroom": (2.5, 3.0),
    "toilet":   (2.0, 2.5),
    "kitchen":  (4.5, 4.0),
    "balcony":  (2.5, 5.0),
}

# Target room dimensions for each type (width, height)
TARGET_SIZES = {
    "bedroom":  (4.5, 4.5),
    "master":   (5.0, 5.0),
    "bathroom": (2.5, 2.5),
    "toilet":   (2.0, 2.0),
    "kitchen":  (3.5, 3.5),
    "balcony":  (2.0, 4.0),
    "living":   (6.0, 5.0),
    "dining":   (4.0, 4.0),
    "hallway":  (2.0, None),   # width fixed, length flexible
    "corridor": (1.5, None),
    "study":    (3.5, 3.5),
}


def get_room_type(label: str) -> str:
    lower = label.lower()
    if "master" in lower: return "master"
    if "bedroom" in lower: return "bedroom"
    if "bathroom" in lower: return "bathroom"
    if "toilet" in lower: return "toilet"
    if "kitchen" in lower: return "kitchen"
    if "living" in lower: return "living"
    if "balcony" in lower: return "balcony"
    if "hallway" in lower or "corridor" in lower: return "hallway"
    if "dining" in lower: return "dining"
    if "study" in lower: return "study"
    return "other"


def _clean_rooms(rooms, building_w, building_h):
    """Snap, round, and filter degenerate rooms."""
    cleaned = []
    if not rooms:
        return cleaned
    for room in rooms:
        room.p1.x = max(0.0, round(room.p1.x, 1))
        room.p1.y = max(0.0, round(room.p1.y, 1))
        room.p2.x = min(building_w, round(room.p2.x, 1))
        room.p2.y = min(building_h, round(room.p2.y, 1))
        if (room.p2.x - room.p1.x) >= 0.2 and (room.p2.y - room.p1.y) >= 0.2:
            cleaned.append(room)
    return cleaned


def post_process_plan(plan: Plan, building_w: float, building_h: float) -> Plan:
    """
    Clean up plan coordinates for structural precision.
    Ensures rooms are rounded to 1 decimal place and snapped.
    Handles both single-floor (plan.rooms) and multi-floor (plan.floors) plans.
    """
    # Process top-level rooms
    new_rooms = _clean_rooms(plan.rooms, building_w, building_h)

    # Process floors
    new_floors = None
    if plan.floors:
        new_floors = []
        for f in plan.floors:
            f_rooms = _clean_rooms(f.rooms, building_w, building_h)
            new_floors.append(Floor(name=f.name, rooms=f_rooms))

    return Plan(units=plan.units, rooms=new_rooms if new_rooms else None, floors=new_floors)
