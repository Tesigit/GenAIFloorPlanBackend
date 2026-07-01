from __future__ import annotations
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from .models import Constraints, GenerateResult, Plan, Room, Point
from .validator import validate_plan
from .generator import get_last_prompt
from .db import get_db
from .auth import hash_password, verify_password, create_access_token, decode_token

# ── Load .env ────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    if os.path.isfile(os.path.join(os.getcwd(), ".env")):
        load_dotenv(os.path.join(os.getcwd(), ".env"))
    else:
        parent_env = os.path.join(os.path.dirname(os.getcwd()), ".env")
        if os.path.isfile(parent_env):
            load_dotenv(parent_env)
except Exception:
    pass

# ── Verify API key ───────────────────────────────────────────
_GROQ_KEY = os.getenv("GROQ_API_KEY")
_OR_KEY   = os.getenv("OPENROUTER_API_KEY")
if _GROQ_KEY:
    print(f"✓ Groq API key loaded (prefix: {_GROQ_KEY[:8]}...)")
elif _OR_KEY:
    print(f"✓ OpenRouter API key loaded (prefix: {_OR_KEY[:12]}...)")
else:
    print("⚠ WARNING: No AI API key found. Will use Layout Engine fallback only.")

# ── App ──────────────────────────────────────────────────────
app = FastAPI(title="GPLAN Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://gen-ai-floor-plan.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
from fastapi.responses import Response

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response()

# ── Request / Response models ────────────────────────────────
class GenerateRequest(BaseModel):
    length: float
    width: float
    floors: int = 1
    floorDetails: Optional[List[Dict[str, Any]]] = None
    bedrooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    livingRooms: int = 0
    balconies: int = 0
    specialRequirements: List[str] = []
    stylePreference: str = "modern"
    prompt: str = ""
    units: str = "meters"

    class Config:
        extra = "ignore"


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SavePlanRequest(BaseModel):
    plan_json: Dict[str, Any]       # The full plan object as JSON
    constraints: Dict[str, Any]     # The constraints used to generate
    title: str = ""
    source: str = "ai"             # "ai" or "fallback"
    messages: List[str] = []


# ── Helper: extract user from Authorization header ───────────
def get_current_user_id(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    return decode_token(token)


# ── Routes ───────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "GPLAN Backend v0.2", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/db/health")
async def db_health():
    db = get_db()
    if db is None:
        return {"connected": False, "reason": "MONGODB_URI not set"}
    try:
        await db.client.admin.command("ping")
        return {"connected": True}
    except Exception as e:
        return {"connected": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════════════════════════
@app.post("/auth/register")
async def register(req: RegisterRequest):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    # Check duplicate email
    existing = await db["users"].find_one({"email": req.email.lower()})
    if existing:
        raise HTTPException(400, "Email already registered")

    user_doc = {
        "name": req.name.strip(),
        "email": req.email.lower().strip(),
        "password_hash": hash_password(req.password),
        "created_at": datetime.utcnow(),
    }
    result = await db["users"].insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token({"sub": user_id})

    return {"token": token, "name": req.name.strip(), "email": req.email.lower().strip()}


@app.post("/auth/login")
async def login(req: LoginRequest):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    user = await db["users"].find_one({"email": req.email.lower()})
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(401, "Invalid email or password")

    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id})
    return {"token": token, "name": user["name"], "email": user["email"]}


# ═══════════════════════════════════════════════════════════
#  PLAN SAVE / RETRIEVE ROUTES
# ═══════════════════════════════════════════════════════════
@app.post("/plans/save")
async def save_plan(req: SavePlanRequest, authorization: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization)
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    doc = {
        "user_id": user_id,           # None = anonymous save
        "plan_json": req.plan_json,
        "constraints": req.constraints,
        "title": req.title or f"{req.constraints.get('bedrooms',0)}BHK Plan",
        "source": req.source,
        "messages": req.messages,
        "created_at": datetime.utcnow(),
    }
    result = await db["plans"].insert_one(doc)
    return {"id": str(result.inserted_id), "message": "Plan saved!"}


@app.get("/plans/my")
async def get_my_plans(authorization: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization)
    if not user_id:
        raise HTTPException(401, "Login required to view your plans")

    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    cursor = db["plans"].find({"user_id": user_id}).sort("created_at", -1).limit(20)
    plans = await cursor.to_list(None)

    result = []
    for p in plans:
        result.append({
            "id": str(p["_id"]),
            "title": p.get("title", "Floor Plan"),
            "source": p.get("source", "ai"),
            "constraints": p.get("constraints", {}),
            "plan_json": p.get("plan_json", {}),
            "messages": p.get("messages", []),
            "created_at": p.get("created_at", datetime.utcnow()).isoformat(),
        })
    return result


@app.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, authorization: Optional[str] = Header(None)):
    from bson import ObjectId
    user_id = get_current_user_id(authorization)
    if not user_id:
        raise HTTPException(401, "Login required")

    db = get_db()
    result = await db["plans"].delete_one({"_id": ObjectId(plan_id), "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Plan not found")
    return {"message": "Deleted"}


# ═══════════════════════════════════════════════════════════
#  GENERATE ROUTE
# ═══════════════════════════════════════════════════════════
@app.post("/generate", response_model=GenerateResult)
async def generate(req: GenerateRequest, authorization: Optional[str] = Header(None)):
    from .generator import generate_plan

    floor_details = []
    if req.floorDetails:
        from .models import FloorConfig
        floor_names = ['Ground Floor'] + [f'Floor {i}' for i in range(1, 10)]
        for i, detail in enumerate(req.floorDetails):
            detail['name'] = floor_names[i] if i < len(floor_names) else f'Floor {i}'
            floor_details.append(FloorConfig(**detail))

    # Compute aggregate room counts from ground floor details (for AI prompt & validator)
    agg_bed = req.bedrooms or (int(floor_details[0].bedrooms) if floor_details else 2)
    agg_bath = req.bathrooms or (int(floor_details[0].bathrooms) if floor_details else 1)
    agg_kit = req.kitchens or (int(floor_details[0].kitchens) if floor_details else 1)
    agg_liv = req.livingRooms or (int(floor_details[0].livingRooms) if floor_details else 1)
    agg_bal = req.balconies or (int(floor_details[0].balconies) if floor_details else 0)

    constraints = Constraints(
        length=req.length, width=req.width, floors=req.floors,
        floorDetails=floor_details,
        bedrooms=agg_bed, bathrooms=agg_bath,
        kitchens=agg_kit, livingRooms=agg_liv,
        balconies=agg_bal, specialRequirements=req.specialRequirements,
        stylePreference=req.stylePreference, prompt=req.prompt,
    )

    messages: List[str] = []

    # Fetch seed plans — match by bedrooms (primary) + style (secondary)
    seed_plans: List[dict] = []
    mongo_uri = os.getenv("MONGODB_URI", "")
    if mongo_uri and "<" not in mongo_uri:
        try:
            db = get_db()
            if db is not None:
                # Try exact match first (same bedrooms + style)
                query = {"bedrooms": req.bedrooms, "style": req.stylePreference}
                seed_plans = await db["seed_plans"].find(query).limit(2).to_list(None)
                if not seed_plans:
                    # Fallback: same bedrooms, any style
                    seed_plans = await db["seed_plans"].find({"bedrooms": req.bedrooms}).limit(2).to_list(None)
                if not seed_plans:
                    # Last resort: any plan of same style
                    seed_plans = await db["seed_plans"].find({"style": req.stylePreference}).limit(2).to_list(None)
                for s in seed_plans:
                    s.pop("_id", None)
                if seed_plans:
                    messages.append(f"📚 Using {len(seed_plans)} reference plan(s) as examples")
        except Exception as e:
            print(f"DB seed lookup skipped: {e}")

    # ── AI generation loop ───────────────────────────────────
    MAX_ITERS = 2
    feedback_history: List[str] = []
    iterations = 0
    final_plan: Optional[Plan] = None
    used_ai = False
    valid = False

    for i in range(MAX_ITERS):
        iterations = i + 1
        try:
            # generate_plan handles API calls and JSON parsing
            temp_plan = generate_plan(constraints, units=req.units,
                                      feedback_history=feedback_history,
                                      example_plans=seed_plans)
            
            # Run structural validation
            v = validate_plan(temp_plan, constraints)
            
            if v.valid:
                valid = True
                final_plan = temp_plan
                used_ai = True
                messages.append("✅ AI Generated — Structural Validation Passed")
                break
            else:
                # Store it as best effort for now, but mark it invalid
                issues = "; ".join([f"{iss.code}: {iss.message}" for iss in v.issues])
                messages.append(f"AI Attempt {iterations} Invalid: {issues}")
                feedback_history.append(issues)
                # Keep the last one in case fallback fails, but we prefer fallback
                final_plan = temp_plan 

        except Exception as e:
            err = str(e)
            print(f"AI generation failed: {err[:200]}")
            messages.append(f"AI Error: {err[:100]}")
            break

    # ── Fallback logic: If AI plan was invalid or failed, use Layout Engine ───
    source = "ai" if (used_ai and valid) else "fallback"

    if not valid:
        messages.append("🔄 AI plan invalid — falling back to high-reliability Layout Engine")
        try:
            from .fallback_plans import generate_fallback_plan
            plot_w = float(req.width)
            plot_h = float(req.length)
            fb_plan = generate_fallback_plan(constraints, plot_w, plot_h, req.prompt, req.specialRequirements)
            if fb_plan:
                final_plan = fb_plan
                source = "fallback"
        except Exception as fe:
            print(f"Fallback engine error: {fe}")
            # If even fallback fails but we had an invalid AI plan, we're in trouble
            if not final_plan:
                raise HTTPException(500, f"Critical Failure: both AI and Fallback failed. {messages[-1]}")

    if final_plan is None:
        raise HTTPException(500, f"Generation failed completely: {'; '.join(messages[-3:])}")

    # ── Post-process (safe — never crashes the response) ─────
    try:
        from .post_processor import post_process_plan
        final_plan = post_process_plan(final_plan, float(req.width), float(req.length))
    except Exception as pe:
        print(f"Post-processor skipped: {pe}")

    # ── Auto-save to DB if user logged in ─────────────────────
    user_id = get_current_user_id(authorization)
    if user_id:
        try:
            db_save = get_db()
            if db_save:
                plan_dict = final_plan.model_dump()
                await db_save["plans"].insert_one({
                    "user_id": user_id,
                    "plan_json": plan_dict,
                    "constraints": constraints.model_dump(),
                    "title": f"{req.bedrooms}BHK {req.width}×{req.length}m",
                    "source": source,
                    "messages": messages,
                    "created_at": datetime.utcnow(),
                })
        except Exception as e:
            print(f"Auto-save failed: {e}")

    return GenerateResult(
        plan=final_plan, iterations=iterations, messages=messages,
        valid=valid, prompt_sent=get_last_prompt(), source=source,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
