"""
Strict floor plan validator v3.
Checks: overlaps, minimum dimensions, room counts, bounds, Pooja adjacency,
        graph-based connectivity, perimeter ventilation, circulation flow.
"""
from __future__ import annotations
from typing import List, Dict, Set
from .models import Plan, Room, Constraints, ValidationResult, ValidationIssue


# Minimum room DIMENSIONS in metres (width × depth)
MIN_DIMS = {
    "bedroom":  (3.0, 3.0),   # 3m × 3m minimum
    "bathroom": (1.5, 1.5),   # 1.5m × 1.5m minimum
    "kitchen":  (2.0, 2.0),   # 2m × 2m minimum
    "living":   (3.0, 3.0),   # 3m × 3m minimum
    "balcony":  (1.0, 1.5),   # small is OK
    "pooja":    (1.2, 1.2),
    "dining":   (2.0, 2.0),
    "study":    (2.0, 2.0),
}

# Rooms classified as "private" — entry path must NOT cross through them
PRIVATE_TYPES = {"bedroom", "bathroom", "pooja"}

# Rooms that require exterior wall for windows & ventilation
HABITABLE_TYPES = {"bedroom", "kitchen", "living", "dining", "study"}


def _room_dims(room: Room) -> tuple:
    w = abs(room.p2.x - room.p1.x)
    d = abs(room.p2.y - room.p1.y)
    return (round(w, 2), round(d, 2))


def _room_type(room: Room) -> str:
    ll = room.label.lower()
    for t in ["stair", "lift", "bedroom", "bathroom", "kitchen", "living",
              "balcony", "pooja", "dining", "study", "garage", "corridor",
              "hallway", "foyer", "store", "utility"]:
        if t in ll:
            return t
    return "other"


def aabb_overlap(r1: Room, r2: Room) -> bool:
    if r1.p2.x <= r2.p1.x + 0.05 or r2.p2.x <= r1.p1.x + 0.05:
        return False
    if r1.p2.y <= r2.p1.y + 0.05 or r2.p2.y <= r1.p1.y + 0.05:
        return False
    return True


def shares_wall(r1: Room, r2: Room) -> bool:
    """True if two rooms are edge-adjacent (share a wall segment ≥ 0.5m)."""
    tol = 0.2
    # Horizontal adjacency (left-right neighbors)
    if abs(r1.p2.x - r2.p1.x) < tol or abs(r2.p2.x - r1.p1.x) < tol:
        oy = min(r1.p2.y, r2.p2.y) - max(r1.p1.y, r2.p1.y)
        if oy > 0.5:
            return True
    # Vertical adjacency (top-bottom neighbors)
    if abs(r1.p2.y - r2.p1.y) < tol or abs(r2.p2.y - r1.p1.y) < tol:
        ox = min(r1.p2.x, r2.p2.x) - max(r1.p1.x, r2.p1.x)
        if ox > 0.5:
            return True
    return False


def has_perimeter_wall(room: Room, plot_w: float, plot_h: float) -> bool:
    """Check if at least one wall of the room sits on the plot boundary."""
    tol = 0.15
    return (
        abs(room.p1.x) < tol or           # West wall
        abs(room.p2.x - plot_w) < tol or   # East wall
        abs(room.p1.y) < tol or            # North wall
        abs(room.p2.y - plot_h) < tol      # South wall
    )


def perimeter_wall_length(room: Room, plot_w: float, plot_h: float) -> float:
    """Total length of room walls that sit on the plot boundary."""
    tol = 0.15
    total = 0.0
    w = abs(room.p2.x - room.p1.x)
    h = abs(room.p2.y - room.p1.y)
    if abs(room.p1.x) < tol: total += h        # West
    if abs(room.p2.x - plot_w) < tol: total += h   # East
    if abs(room.p1.y) < tol: total += w        # North
    if abs(room.p2.y - plot_h) < tol: total += w   # South
    return total


def build_adjacency_graph(rooms: List[Room]) -> Dict[int, Set[int]]:
    """Build an adjacency graph where connected rooms share a wall."""
    graph: Dict[int, Set[int]] = {i: set() for i in range(len(rooms))}
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            if shares_wall(rooms[i], rooms[j]):
                graph[i].add(j)
                graph[j].add(i)
    return graph


def find_entry_node(rooms: List[Room]) -> int:
    """Find the best entry point: Foyer > Corridor > Living Room."""
    for i, r in enumerate(rooms):
        if "foyer" in r.label.lower() or "entry" in r.label.lower():
            return i
    for i, r in enumerate(rooms):
        if _room_type(r) in ("corridor", "hallway"):
            return i
    for i, r in enumerate(rooms):
        if _room_type(r) == "living":
            return i
    return 0


def check_connectivity(rooms: List[Room], graph: Dict[int, Set[int]]) -> List[int]:
    """
    BFS from entry node through public spaces only.
    Returns list of room indices that are NOT reachable.
    Private rooms (bedrooms, bathrooms) can be reached but NOT traversed through.
    """
    entry = find_entry_node(rooms)
    reachable: Set[int] = {entry}
    queue = [entry]

    while queue:
        curr = queue.pop(0)
        curr_type = _room_type(rooms[curr])

        # Don't traverse THROUGH private rooms (but they are reachable)
        if curr_type in PRIVATE_TYPES and curr != entry:
            continue

        for neighbor in graph[curr]:
            if neighbor not in reachable:
                reachable.add(neighbor)
                queue.append(neighbor)

    # Find unreachable rooms (excluding structural elements)
    unreachable = []
    skip_types = {"stair", "lift", "garage", "balcony"}
    for i, r in enumerate(rooms):
        rt = _room_type(r)
        if i not in reachable and rt not in skip_types:
            unreachable.append(i)

    return unreachable


def check_entry_flow(rooms: List[Room], graph: Dict[int, Set[int]]) -> List[str]:
    """
    Verify: Entry → Foyer → Living (not Bedroom/Bathroom first).
    The first room encountered from entry should NOT be a private room.
    """
    issues = []
    entry_idx = find_entry_node(rooms)
    entry_type = _room_type(rooms[entry_idx])

    if entry_type in PRIVATE_TYPES:
        issues.append(f"Entry point is a {entry_type} ('{rooms[entry_idx].label}'). "
                      f"Main entry must lead to a Foyer or Living Room, not a private space.")
        return issues

    # Check if immediate neighbors of entry include a bedroom/bathroom BEFORE living
    neighbors = graph.get(entry_idx, set())
    has_public_neighbor = False
    for n in neighbors:
        nt = _room_type(rooms[n])
        if nt in ("living", "corridor", "hallway", "dining"):
            has_public_neighbor = True

    if not has_public_neighbor and len(neighbors) > 0:
        neighbor_types = [_room_type(rooms[n]) for n in neighbors]
        if all(t in PRIVATE_TYPES for t in neighbor_types):
            issues.append(f"Entry flows directly into private rooms ({neighbor_types}). "
                          f"It must connect to a public space (Living Room, Corridor) first.")

    return issues


def count_rooms_by_type(rooms: List[Room]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for room in rooms:
        rt = _room_type(room)
        counts[rt] = counts.get(rt, 0) + 1
    return counts


def validate_plan(plan: Plan, constraints: Constraints = None) -> ValidationResult:
    issues: List[ValidationIssue] = []
    rooms = plan.rooms or []

    if not rooms:
        issues.append(ValidationIssue(code="EMPTY", message="Plan has no rooms."))
        return ValidationResult(valid=False, issues=issues)

    pw = float(constraints.width) if constraints else 0
    pd = float(constraints.length) if constraints else 0

    # ── 1. OVERLAP CHECK ──────────────────────────────────────────────────
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            if aabb_overlap(rooms[i], rooms[j]):
                issues.append(ValidationIssue(
                    code="OVERLAP",
                    message=f"STRUCTURAL FAILURE: '{rooms[i].label}' overlaps '{rooms[j].label}'.",
                    room_indices=[i, j],
                ))

    # ── 2. MINIMUM DIMENSION CHECK ────────────────────────────────────────
    for idx, room in enumerate(rooms):
        rt = _room_type(room)
        w, d = _room_dims(room)

        if w < 0.5 or d < 0.5:
            issues.append(ValidationIssue(
                code="DEGENERATE",
                message=f"'{room.label}' has degenerate size {w}×{d}m",
                room_indices=[idx],
            ))
            continue

        if rt in MIN_DIMS:
            min_w, min_d = MIN_DIMS[rt]
            dim_ok = (w >= min_w - 0.1 and d >= min_d - 0.1) or \
                     (w >= min_d - 0.1 and d >= min_w - 0.1)
            if not dim_ok:
                issues.append(ValidationIssue(
                    code="TOO_SMALL",
                    message=f"'{room.label}' is {w:.1f}×{d:.1f}m — minimum {min_w}×{min_d}m",
                    room_indices=[idx],
                ))

    # ── 3. PERIMETER VENTILATION CHECK ────────────────────────────────────
    # Every habitable room MUST touch at least one exterior wall.
    if pw > 0 and pd > 0:
        for idx, room in enumerate(rooms):
            rt = _room_type(room)
            if rt in HABITABLE_TYPES and not has_perimeter_wall(room, pw, pd):
                issues.append(ValidationIssue(
                    code="VENTILATION_ERROR",
                    message=f"'{room.label}' has 0m of exterior wall — it's a dark room with no windows. "
                            f"Every habitable room must touch the plot boundary.",
                    room_indices=[idx],
                ))

    # ── 4. GRAPH-BASED CONNECTIVITY ───────────────────────────────────────
    graph = build_adjacency_graph(rooms)
    unreachable = check_connectivity(rooms, graph)
    for idx in unreachable:
        issues.append(ValidationIssue(
            code="LANDLOCKED",
            message=f"CIRCULATION FAILURE: '{rooms[idx].label}' is unreachable from the Entry. "
                    f"All rooms must connect via public spaces (corridors, foyer, living).",
            room_indices=[idx],
        ))

    # ── 5. ENTRY FLOW CHECK ───────────────────────────────────────────────
    flow_issues = check_entry_flow(rooms, graph)
    for msg in flow_issues:
        issues.append(ValidationIssue(code="ENTRY_FLOW", message=msg))

    # ── 6. KITCHEN-DINING ADJACENCY ───────────────────────────────────────
    kitchens = [i for i, r in enumerate(rooms) if _room_type(r) == "kitchen"]
    dinings = [i for i, r in enumerate(rooms) if _room_type(r) == "dining"]
    if kitchens and dinings:
        is_adjacent = any(
            shares_wall(rooms[k], rooms[d])
            for k in kitchens for d in dinings
        )
        if not is_adjacent:
            issues.append(ValidationIssue(
                code="ADJACENCY_VIOLATION",
                message="Kitchen and Dining must be adjacent (share a wall).",
            ))

    # ── 7. POOJA ROOM VALIDATION ──────────────────────────────────────────
    for idx, room in enumerate(rooms):
        if "pooja" in room.label.lower():
            w, d = _room_dims(room)
            if w > 3.0 or d > 3.0:
                issues.append(ValidationIssue(
                    code="INVALID_POOJA",
                    message=f"Pooja room is {w}×{d}m — too large. Max 3×3m.",
                    room_indices=[idx],
                ))
            # Pooja must NOT share wall with bathroom
            for oidx, other in enumerate(rooms):
                if _room_type(other) == "bathroom" and shares_wall(room, other):
                    issues.append(ValidationIssue(
                        code="POOJA_BATHROOM",
                        message=f"Pooja Room shares a wall with '{other.label}'. "
                                f"Vastu: Pooja must never be adjacent to a bathroom.",
                        room_indices=[idx, oidx],
                    ))

    # ── 8. ROOM COUNT VALIDATION ──────────────────────────────────────────
    if constraints:
        counts = count_rooms_by_type(rooms)
        if counts.get("bedroom", 0) < constraints.bedrooms:
            issues.append(ValidationIssue(
                code="MISSING_BEDROOM",
                message=f"Missing {constraints.bedrooms - counts.get('bedroom', 0)} bedrooms.",
            ))

    # ── 9. GAP / COVERAGE CHECK ───────────────────────────────────────────
    if constraints and pw > 0 and pd > 0:
        plot_area = pw * pd
        total_area = sum(_room_dims(r)[0] * _room_dims(r)[1] for r in rooms)
        utilization = total_area / plot_area if plot_area > 0 else 0
        if utilization < 0.90:
            issues.append(ValidationIssue(
                code="GAP_DETECTED",
                message=f"Plan utilizes {utilization*100:.1f}% of plot area. Minimum 90%.",
            ))

    return ValidationResult(valid=len(issues) == 0, issues=issues)
