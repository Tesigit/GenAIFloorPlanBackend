"""
Professional fallback floor plan engine v6 — Core-First Design Strategy.

Architecture: NBC 2016 + Vastu-Compliant, Circulation-Spine layout.

Design Philosophy:
  1. CORE FIRST: Fix staircase+lift at SW corner.
  2. SPINE SECOND: Lay a 1.2m circulation corridor connecting entry to all zones.
  3. ROOMS LAST: Fill zones along perimeter walls — every room has exterior access.

Vastu Mapping (Coordinate System):
  x=0 → West,  x=W → East
  y=0 → North, y=H → South

  NE corner = (W, 0)  — Pooja Room, Living Room
  SE corner = (W, H)  — Kitchen
  SW corner = (0, H)  — Staircase, Master Bedroom
  NW corner = (0, 0)  — Bathrooms

Guarantee: Every habitable room touches at least one plot boundary wall.
"""

from typing import List, Dict


def _build_layout(
    building_w: float,
    building_h: float,
    bedrooms: int,
    bathrooms: int,
    kitchens: int,
    living_rooms: int,
    balconies: int,
    has_parking: bool = False,
    has_staircase: bool = False,
    has_lift: bool = False,
    prompt: str = "",
    special_reqs: list = None,
) -> List[Dict]:
    rooms: List[Dict] = []
    W = round(building_w, 1)
    H = round(building_h, 1)

    prompt_low = (prompt or "").lower()
    needs_pooja = "pooja" in prompt_low or "puja" in prompt_low or "vastu" in prompt_low
    needs_balcony = balconies > 0 or "balcony" in prompt_low

    # ══════════════════════════════════════════════════════════════
    #  PHASE 1: STRUCTURAL CORE — South-West (Vastu)
    # ══════════════════════════════════════════════════════════════
    STAIR_W = 2.5
    STAIR_H = 3.5
    LIFT_W = 1.5
    LIFT_H = 1.5
    core_w = 0.0   # total width consumed by core elements at SW
    core_h = 3.5   # height of the south strip (entry + core)

    if has_staircase:
        rooms.append({
            "label": "Staircase",
            "p1": {"x": 0, "y": H - STAIR_H},
            "p2": {"x": STAIR_W, "y": H},
            "metadata": {"type": "stair"},
        })
        core_w = STAIR_W
        if has_lift:
            rooms.append({
                "label": "Lift Core",
                "p1": {"x": STAIR_W, "y": H - LIFT_H},
                "p2": {"x": STAIR_W + LIFT_W, "y": H},
                "metadata": {"type": "lift"},
            })
            core_w = STAIR_W + LIFT_W

    # ══════════════════════════════════════════════════════════════
    #  PHASE 2: ENTRY ZONE — South strip with clear landing
    # ══════════════════════════════════════════════════════════════
    if has_parking:
        rooms.append({
            "label": "Parking Garage",
            "p1": {"x": core_w, "y": H - core_h},
            "p2": {"x": W, "y": H},
            "metadata": {"type": "garage"},
        })
    else:
        rooms.append({
            "label": "Entry Foyer",
            "p1": {"x": core_w, "y": H - core_h},
            "p2": {"x": W, "y": H},
            "metadata": {"type": "other"},
        })

    # ══════════════════════════════════════════════════════════════
    #  PHASE 3: AVAILABLE ZONE (above entry strip)
    # ══════════════════════════════════════════════════════════════
    avail_y0 = 0.0                   # top edge (North)
    avail_y1 = round(H - core_h, 1) # bottom edge (just above entry)
    avail_h = round(avail_y1 - avail_y0, 1)

    # ══════════════════════════════════════════════════════════════
    #  PHASE 4: BALCONY — North perimeter (if needed)
    # ══════════════════════════════════════════════════════════════
    BALC_H = 0.0
    if needs_balcony:
        BALC_H = 1.5 if avail_h > 8.0 else 1.0
        rooms.append({
            "label": "Balcony",
            "p1": {"x": 0, "y": 0},
            "p2": {"x": W, "y": BALC_H},
            "metadata": {"type": "balcony"},
        })
        avail_y0 = BALC_H
        avail_h = round(avail_y1 - avail_y0, 1)

    # ══════════════════════════════════════════════════════════════
    #  PHASE 5: TWO-COLUMN LAYOUT with Circulation Corridor
    # ══════════════════════════════════════════════════════════════
    CORR_W = 1.2
    left_w = round((W - CORR_W) * 0.42, 1)
    right_w = round(W - left_w - CORR_W, 1)
    # Adjust widths to guarantee min 3.0 for bedrooms if possible
    if left_w < 3.0 and W > 5.0: left_w = 3.0
    if right_w < 3.0 and W > 5.0: right_w = 3.0
    
    corr_x0 = left_w
    corr_x1 = round(left_w + CORR_W, 1)
    right_x0 = corr_x1

    if W < 5.0:
        CORR_W = 0
        left_w = round(W * 0.45, 1)
        right_w = round(W - left_w, 1)
        corr_x0 = corr_x1 = right_x0 = left_w
    else:
        rooms.append({
            "label": "Corridor",
            "p1": {"x": corr_x0, "y": avail_y0},
            "p2": {"x": corr_x1, "y": avail_y1},
            "metadata": {"type": "hallway"},
        })

    # ── LEFT COLUMN: LIVING (top) → BATH (mid) → MASTER BED (bottom) ──
    # Allocate heights from bottom up to guarantee Master Bedroom gets 3.0m
    master_h = 3.0 if avail_h >= 6.0 else (avail_h * 0.4)
    mb_start_y = round(avail_y1 - master_h, 1)

    # Optional bath above master bed
    left_bath_h = 0.0
    if bathrooms > 0 and avail_h >= 8.0:
        left_bath_h = 1.5
        bath_start_y = round(mb_start_y - left_bath_h, 1)
        rooms.append({
            "label": "Master Bath",
            "p1": {"x": 0, "y": bath_start_y},
            "p2": {"x": left_w, "y": mb_start_y},
            "metadata": {"type": "bathroom"}
        })
        live_end_y = bath_start_y
    else:
        live_end_y = mb_start_y

    # Master Bedroom
    rooms.append({
        "label": "Master Bedroom",
        "p1": {"x": 0, "y": mb_start_y},
        "p2": {"x": left_w, "y": avail_y1},
        "metadata": {"type": "bedroom"},
    })

    # Living Room takes remainder
    if live_end_y > avail_y0:
        rooms.append({
            "label": "Living Room",
            "p1": {"x": 0, "y": avail_y0},
            "p2": {"x": left_w, "y": live_end_y},
            "metadata": {"type": "living"},
        })

    # ── RIGHT COLUMN: POOJA/ENTRY (NE) → KITCHEN → DINING → BATH → BEDROOMS ──
    right_y_cursor = avail_y0

    if needs_pooja:
        pj_w = min(1.8, right_w * 0.4)
        pj_h = 1.5
        rooms.append({
            "label": "Pooja Room",
            "p1": {"x": W - pj_w, "y": right_y_cursor},
            "p2": {"x": W, "y": round(right_y_cursor + pj_h, 1)},
            "metadata": {"type": "pooja"},
        })
        if right_w - pj_w > 1.0:
            rooms.append({
                "label": "Entry Hall",
                "p1": {"x": right_x0, "y": right_y_cursor},
                "p2": {"x": round(W - pj_w, 1), "y": round(right_y_cursor + pj_h, 1)},
                "metadata": {"type": "other"},
            })
        right_y_cursor = round(right_y_cursor + pj_h, 1)

    # We have some height left. Distribute it strictly.
    remaining_h = round(avail_y1 - right_y_cursor, 1)
    
    # Calculate required heights
    req_kitchen = 2.0 if kitchens > 0 else 0.0
    req_dining = 2.0 if remaining_h > 5.0 else 0.0 # Only if space permits
    req_bath = 1.5 if bathrooms > 1 else 0.0
    extra_beds = max(0, bedrooms - 1)
    req_beds = extra_beds * 3.0

    total_req = req_kitchen + req_dining + req_bath + req_beds

    # Scale proportionally if we don't have enough space
    scale = remaining_h / total_req if total_req > 0 and total_req > remaining_h else 1.0

    if kitchens > 0:
        h = round(req_kitchen * scale, 1)
        rooms.append({
            "label": "Kitchen",
            "p1": {"x": right_x0, "y": right_y_cursor},
            "p2": {"x": W, "y": round(right_y_cursor + h, 1)},
            "metadata": {"type": "kitchen"},
        })
        right_y_cursor = round(right_y_cursor + h, 1)

    if req_dining > 0:
        h = round(req_dining * scale, 1)
        rooms.append({
            "label": "Dining Area",
            "p1": {"x": right_x0, "y": right_y_cursor},
            "p2": {"x": W, "y": round(right_y_cursor + h, 1)},
            "metadata": {"type": "dining"},
        })
        right_y_cursor = round(right_y_cursor + h, 1)

    if req_bath > 0:
        h = round(req_bath * scale, 1)
        rooms.append({
            "label": "Bathroom 2",
            "p1": {"x": right_x0, "y": right_y_cursor},
            "p2": {"x": W, "y": round(right_y_cursor + h, 1)},
            "metadata": {"type": "bathroom"},
        })
        right_y_cursor = round(right_y_cursor + h, 1)

    # Extra bedrooms
    if extra_beds > 0:
        h = round((avail_y1 - right_y_cursor) / extra_beds, 1)
        for i in range(extra_beds):
            by1 = round(right_y_cursor + i * h, 1)
            by2 = round(right_y_cursor + (i + 1) * h, 1) if i < extra_beds - 1 else avail_y1
            rooms.append({
                "label": f"Bedroom {i + 2}",
                "p1": {"x": right_x0, "y": by1},
                "p2": {"x": W, "y": by2},
                "metadata": {"type": "bedroom"},
            })

    # Round all coordinates
    for r in rooms:
        for pt in ["p1", "p2"]:
            r[pt]["x"] = round(r[pt]["x"], 1)
            r[pt]["y"] = round(r[pt]["y"], 1)

    return rooms


def generate_fallback_plan(constraints, plot_w: float, plot_h: float, prompt: str = "", special_reqs: list = None):
    from .models import Floor, Plan, Room, Point, FloorConfig

    num_floors = getattr(constraints, 'floors', 1)
    details = list(getattr(constraints, 'floorDetails', []) or [])

    # Pad details if missing
    while len(details) < num_floors:
        idx = len(details)
        name = "Ground Floor" if idx == 0 else f"Floor {idx}"
        details.append(FloorConfig(
            name=name,
            bedrooms=constraints.bedrooms if idx == 0 else max(1, constraints.bedrooms),
            bathrooms=constraints.bathrooms,
            kitchens=constraints.kitchens if idx == 0 else 0,
            livingRooms=constraints.livingRooms if idx == 0 else max(0, constraints.livingRooms - 1),
            balconies=constraints.balconies,
            parking=(idx == 0),
            hasLift=False,
        ))

    parsed_floors = []
    has_staircase = num_floors > 1

    for idx, fd in enumerate(details[:num_floors]):
        layout_dicts = _build_layout(
            building_w=plot_w,
            building_h=plot_h,
            bedrooms=fd.bedrooms,
            bathrooms=fd.bathrooms,
            kitchens=fd.kitchens,
            living_rooms=fd.livingRooms,
            balconies=fd.balconies,
            has_parking=fd.parking and idx == 0,  # Only ground floor gets parking
            has_staircase=has_staircase,
            has_lift=getattr(fd, 'hasLift', False),
            prompt=prompt if idx == 0 else "",
            special_reqs=special_reqs,
        )

        floor_rooms = []
        for r_dict in layout_dicts:
            floor_rooms.append(Room(
                label=r_dict["label"],
                p1=Point(x=r_dict["p1"]["x"], y=r_dict["p1"]["y"]),
                p2=Point(x=r_dict["p2"]["x"], y=r_dict["p2"]["y"]),
                metadata=r_dict.get("metadata", {})
            ))

        parsed_floors.append(Floor(name=fd.name, rooms=floor_rooms))

    return Plan(
        units="meters",
        floors=parsed_floors,
        rooms=parsed_floors[0].rooms if parsed_floors else [],
    )
