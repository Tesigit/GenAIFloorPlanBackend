from __future__ import annotations
import os, json, time, math, random
from typing import List
from .models import Plan, Room, Point, Constraints
try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False
    import urllib.request, urllib.error, ssl

_last_prompt: str = ""
def get_last_prompt() -> str:
    return _last_prompt

# ── SYSTEM & ARCHITECTURAL INSTRUCTIONS ──────────────────────────────────────
# ── SYSTEM & ARCHITECTURAL INSTRUCTIONS ──────────────────────────────────────
SYSTEM_INSTRUCTION = """Final Architectural Directives: Open-Concept Spatial Flow
We are pivoting from simple Drafting layouts to high-end 'Architectural' layout logic.

1. The 'Zero-Corridor' Mandate:
- Abolish Hallways: Do NOT generate dedicated corridors or passages. Instead, use the Living Room and Dining Area as the 'Central Distribution Hub.'
- Direct Access: Every bedroom door must open directly onto the central social hub. This maximizes usable square footage and eliminates dead space.

2. Spatial Interlocking:
- Tetris, not Grid: Instead of a simple grid, use 'L-shaped' or 'T-shaped' room interlocking. This allows the Kitchen to be semi-open to the Dining area.
- Shared Plumbing Wall: Align the Bathroom and Kitchen back-to-back. This is the 'Wet Core' of the house. It is a technical constraint that proves you understand real construction.

3. Dynamic Scaling (Modern Layouts):
- Prioritize a LARGE Living/Dining 'Great Room' and keep the bedrooms compact. This is how modern premium apartments are designed.
- Exterior Exposure: Every single room (including Bathrooms) MUST have at least one wall on the plot perimeter for windows. No 'landlocked' rooms in the center.

4. Refinement Strategy & Geometric Constraints:
- No Corridors: If the plan has dedicated 'Passage' or 'Hallway', it will be rejected as 'Inefficient'.
- Snap-to-Edge: All rooms must snap to each other with Zero Gap. Use the exact same coordinate for shared walls.
- No Overlaps: Hard-coded check: R1.x2 <= R2.x1 or R1.x1 >= R2.x2.
- Aspect Ratio: Keep room width-to-depth ratios between 1:1 and 1:1.5.
"""

STYLE_PROMPTS = {
    "modern":      "STYLE: Modern Open-Plan — minimize internal walls between Living and Dining. Use the Living room as the main hub.",
    "minimalist":  "STYLE: Minimalist — compact, highly aligned structural grid.",
    "traditional": "STYLE: Traditional Vastu — Kitchen SE, Master SW, Pooja NE.",
    "luxury":      "STYLE: Luxury — include Wide Verandahs and spacious en-suites.",
}

# (OpenRouter / Groq HTTP calls remain the same)
def _call_ai(prompt_text: str) -> str:
    """Call Groq (primary) → OpenRouter (fallback)."""
    google_key = os.getenv("GOOGLE_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    or_key   = os.getenv("OPENROUTER_API_KEY", "")

    def _post(url, headers, body, timeout):
        if _HAS_REQUESTS:
            r = _requests.post(url, json=body, headers=headers, timeout=timeout, verify=False)
            r.raise_for_status()
            return r.text
        else:
            ctx = ssl._create_unverified_context()
            raw = json.dumps(body).encode()
            req = urllib.request.Request(url, data=raw, headers={**headers, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return r.read().decode()

    # ── Gemini (Primary) ──
    if google_key:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={google_key}"
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{prompt_text}"
        body = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }
        headers = {"Content-Type": "application/json"}
        for attempt in range(2):
            try:
                text = _post(url, headers, body, timeout=45)
                result = json.loads(text)
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ Gemini (2.5-flash) responded ({len(content)} chars)")
                return content.strip()
            except Exception as e:
                print(f"Gemini attempt {attempt+1}: {str(e)[:150]}")
                if attempt == 0: time.sleep(6)
                continue

    # ── Groq ──
    if groq_key:
        url   = "https://api.groq.com/openai/v1/chat/completions"
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        body  = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user",   "content": prompt_text},
            ],
            "temperature": 0.1,
            "max_tokens":  4096,
        }
        headers = {"Authorization": f"Bearer {groq_key}", "User-Agent": "GPlan/1.0", "Content-Type": "application/json"}
        for attempt in range(2):
            try:
                text = _post(url, headers, body, timeout=45)
                result = json.loads(text)
                content = result["choices"][0]["message"]["content"]
                print(f"✅ Groq ({model}) responded ({len(content)} chars)")
                return content.strip()
            except Exception as e:
                print(f"Groq attempt {attempt+1}: {str(e)[:150]}")
                if ("429" in str(e) or "rate" in str(e).lower()) and attempt == 0:
                    time.sleep(6); continue
                break

    # ── OpenRouter ──
    if or_key:
        url   = "https://openrouter.ai/api/v1/chat/completions"
        model = "meta-llama/llama-3.3-70b-instruct:free"
        body  = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user",   "content": prompt_text},
            ],
            "temperature": 0.1, "max_tokens": 4096,
        }
        headers = {"Authorization": f"Bearer {or_key}", "HTTP-Referer": "http://localhost:5173", "X-Title": "GPlan", "Content-Type": "application/json"}
        for attempt in range(2):
            try:
                text = _post(url, headers, body, timeout=50)
                result = json.loads(text)
                content = result["choices"][0]["message"]["content"]
                print(f"✅ OpenRouter ({model}) responded ({len(content)} chars)")
                return content.strip()
            except Exception as e:
                print(f"OpenRouter attempt {attempt+1}: {str(e)[:100]}")
                if attempt < 1: time.sleep(5)
                else: break

    raise RuntimeError("ALL_APIS_FAILED: No AI key or all APIs unavailable")


def _parse_user_prompt(prompt: str) -> dict:
    result = {"extra_rooms": [], "layout_notes": [], "open_kitchen": False}
    lower  = (prompt or "").lower().strip()
    if not lower:
        return result
    kw_map = {
        "pooja":   ("Pooja Room",   "pooja"),
        "puja":    ("Pooja Room",   "pooja"),
        "prayer":  ("Prayer Room",  "pooja"),
        "study":   ("Study Room",   "study"),
        "office":  ("Home Office",  "study"),
        "dining":  ("Dining Room",  "dining"),
        "store":   ("Store Room",   "utility"),
        "garage":  ("Garage",       "garage"),
        "parking": ("Parking Area", "garage"),
    }
    for kw, (label, rtype) in kw_map.items():
        if kw in lower:
            result["extra_rooms"].append({"label": label, "type": rtype})
    if "open kitchen" in lower:
        result["open_kitchen"] = True
    if "vastu" in lower:
        result["layout_notes"].append("Mandatory Vastu placement.")
    if prompt.strip():
        result["layout_notes"].append(f"Client Note: {prompt.strip()}")
    return result


def _build_prompt(c: Constraints, feedback_history: List[str] = None, example_plans: List[dict] = None) -> str:
    W = round(float(c.width),   1)
    D = round(float(c.length),  1)
    
    style  = STYLE_PROMPTS.get(c.stylePreference.lower(), "")
    parsed = _parse_user_prompt(c.prompt or "")

    floors_text = ""
    json_format = '{"rooms": [ {"label": "...", "p1": {"x":0,"y":0}, "p2": {"x":5,"y":5}} ]}'
    if getattr(c, 'floors', 1) > 1:
        floor_names = ["Ground Floor"] + [f"Floor {i}" for i in range(1, getattr(c, 'floors', 1))]
        names_str = ", ".join(floor_names)
        floors_text = f"MULTI-FLOOR DESIGN: Generate {c.floors} floors ({names_str}). CRITICAL: Every floor MUST have a 'Staircase' room located at the EXACT same geographic (x, y) coordinates so the structural core aligns! Ground floor has Living/Kitchen/Dining, upper floors are for Bedrooms.\n"
        json_format = '{"floors": [ {"name": "Ground Floor", "rooms": [{"label": "...", "p1": {"x":0,"y":0}, "p2": {"x":5,"y":5}}]}, {"name": "Floor 1", "rooms": [...]} ]}'

    prompt = f"""Task: Generate a house plan for a {W}m × {D}m plot.

ARCHITECTURE COMMANDS:
1. FULL FOOTPRINT: Occupy the full {W}x{D} area. NO GARDENS. Scale rooms to fill the plot seamlessly.
2. ZERO-CORRIDOR & WET CORE: NO hallways. Bedrooms open directly to Living. Bathroom and Kitchen MUST share a wall.
3. FINAL TASK: Regenerate the plan using Central Great Room layout. Kitchen, Dining, and Living form a continuous 'L' shape, with bedrooms/baths tucked into the corners. Ensure 0 passage space.

{floors_text}ROOM LIST:
- {c.livingRooms} Living Room (Main Entry, Huge area)
- {c.kitchens} Kitchen (Shares wall with Bathroom)
- 1 Dining Area (Adjacent to Kitchen)
- {c.bedrooms} Bedroom(s)
- {c.bathrooms} Bathroom(s)
{chr(10).join('- 1 ' + r['label'] for r in parsed['extra_rooms'])}

COORDINATES:
- p1 (top-left), p2 (bottom-right). Rectangular only.
- Plot bounds: (0,0) to ({W},{D}).

{style}

USER SPECIFIC NOTES:
{chr(10).join('- ' + n for n in parsed['layout_notes']) if parsed['layout_notes'] else "None"}

Output ONLY valid JSON: {json_format}"""


    if feedback_history:
        prompt += "\n\nCRITICAL FIXES NEEDED:\n" + "\n".join(f"- {f}" for f in feedback_history[-3:])

    return prompt


def generate_plan(constraints: Constraints, units: str = "meters",
                  feedback_history: List[str] = None,
                  example_plans: List[dict] = None) -> Plan:
    global _last_prompt
    prompt = _build_prompt(constraints, feedback_history, example_plans)
    _last_prompt = prompt
    raw = _call_ai(prompt)

    # Parse JSON
    try:
        data = json.loads(raw)
    except Exception:
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(raw[start:end])
        else:
            raise ValueError(f"No JSON in AI response: {raw[:300]}")

    def _parse_room(r_data):
        room = Room(
            label=r_data["label"],
            p1=Point(x=float(r_data["p1"]["x"]), y=float(r_data["p1"]["y"])),
            p2=Point(x=float(r_data["p2"]["x"]), y=float(r_data["p2"]["y"])),
            metadata=r_data.get("metadata", {}),
        )
        if not room.metadata.get("type"):
            ll = room.label.lower()
            for t in ["bedroom","bathroom","kitchen","living","balcony","pooja","dining","study","garage","utility","stair"]:
                if t in ll:
                    room.metadata["type"] = t
                    break
        return room

    from .models import Floor
    
    # Check for floors first
    if "floors" in data and isinstance(data["floors"], list):
        parsed_floors = []
        for f in data["floors"]:
            name = f.get("name", "Floor")
            floor_rooms = []
            for r in f.get("rooms", []):
                try:
                    floor_rooms.append(_parse_room(r))
                except Exception as ex:
                    print(f"Skipping room: {r} — {ex}")
            if floor_rooms:
                parsed_floors.append(Floor(name=name, rooms=floor_rooms))
        
        if not parsed_floors:
            raise ValueError("All floors invalid")
            
        return Plan(units=units, floors=parsed_floors, rooms=parsed_floors[0].rooms)
        
    # Single floor parsing
    rooms_data = data.get("rooms", [])
    if not rooms_data:
        raise ValueError(f"Empty rooms in AI response")

    rooms = []
    for r in rooms_data:
        try:
            rooms.append(_parse_room(r))
        except Exception as ex:
            print(f"Skipping room: {r} — {ex}")
    if not rooms:
        raise ValueError("All rooms invalid")

    parsed_floors = [Floor(name="Ground Floor", rooms=rooms)]
    return Plan(units=units, rooms=rooms, floors=parsed_floors)
