"""Test Gemini API directly with a simple 2BHK plan request."""
import os
from dotenv import load_dotenv
load_dotenv()

from app.generator import generate_plan
from app.models import Constraints

def test():
    key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or ""
    print(f"API Key: {key[:10]}...")
    
    constraints = Constraints(
        length=12.0,
        width=8.0,
        bedrooms=2,
        bathrooms=2,
        kitchens=1,
        livingRooms=1,
        balconies=1,
        specialRequirements=[],
        stylePreference="modern",
        prompt="attached bathrooms to bedrooms, pooja room near living room",
        units="meters"
    )
    
    print("Sending request to Gemini 2.0 Flash...")
    try:
        plan = generate_plan(constraints)
        if plan and plan.rooms:
            print(f"\n✅ SUCCESS! Got {len(plan.rooms)} rooms:")
            for r in plan.rooms:
                w = abs(r.p2.x - r.p1.x)
                h = abs(r.p2.y - r.p1.y)
                print(f"  - {r.label}: {w:.1f}x{h:.1f}m ({w*h:.1f}m²) at ({r.p1.x},{r.p1.y})-({r.p2.x},{r.p2.y})")
        else:
            print("❌ No rooms in plan")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test()
