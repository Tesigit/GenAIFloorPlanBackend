"""
Seed 20 high-quality reference floor plans into MongoDB.
Run: python seed_plans.py
"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from motor.motor_asyncio import AsyncIOMotorClient

PLANS = [
    # ─────────────────────────  8×14 — 2BHK Modern  ─────────────────────────
    {
        "style": "modern", "bedrooms": 2, "bathrooms": 2, "plot_w": 8, "plot_d": 14,
        "title": "8×14 — 2BHK Modern (112m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 5, "y": 6},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 5,   "y": 0},  "p2": {"x": 8, "y": 6},  "metadata": {"type": "kitchen"}},
            {"label": "Corridor",       "p1": {"x": 0,   "y": 6},  "p2": {"x": 8, "y": 8},  "metadata": {"type": "corridor"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 8},  "p2": {"x": 5, "y": 14}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 5,   "y": 8},  "p2": {"x": 6.5,"y":14}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6.5, "y": 8},  "p2": {"x": 8, "y": 14}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  8×15 — 3BHK Modern  ─────────────────────────
    {
        "style": "modern", "bedrooms": 3, "bathrooms": 3, "plot_w": 8, "plot_d": 15,
        "title": "8×15 — 3BHK Modern (120m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 4.5,"y": 6}, "metadata": {"type": "living"}},
            {"label": "Open Kitchen",   "p1": {"x": 4.5, "y": 0},  "p2": {"x": 8, "y": 6},  "metadata": {"type": "kitchen"}},
            {"label": "Corridor",       "p1": {"x": 0,   "y": 6},  "p2": {"x": 8, "y": 7},  "metadata": {"type": "corridor"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 7},  "p2": {"x": 4, "y": 15}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4,   "y": 7},  "p2": {"x": 5.5,"y":15}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 5.5, "y": 7},  "p2": {"x": 8, "y": 11}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 5.5, "y": 11}, "p2": {"x": 8, "y": 13}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 5.5, "y": 13}, "p2": {"x": 8, "y": 15}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  10×12 — 3BHK with Pooja  ────────────────────
    {
        "style": "traditional", "bedrooms": 3, "bathrooms": 3, "plot_w": 10, "plot_d": 12,
        "title": "10×12 — 3BHK Vastu (120m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 6,  "y": 5},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 6,   "y": 0},  "p2": {"x": 10, "y": 5},  "metadata": {"type": "kitchen"}},
            {"label": "Pooja Room",     "p1": {"x": 0,   "y": 5},  "p2": {"x": 2.5,"y": 7},  "metadata": {"type": "pooja"}},
            {"label": "Corridor",       "p1": {"x": 2.5, "y": 5},  "p2": {"x": 10, "y": 7},  "metadata": {"type": "corridor"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 7},  "p2": {"x": 4,  "y": 12}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4,   "y": 7},  "p2": {"x": 5.5,"y": 12}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 5.5, "y": 7},  "p2": {"x": 8,  "y": 12}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 8,   "y": 7},  "p2": {"x": 10, "y": 9.5},"metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 8,   "y": 9.5},"p2": {"x": 10, "y": 12}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  6×8 — 1BHK Compact  ─────────────────────────
    {
        "style": "minimalist", "bedrooms": 1, "bathrooms": 1, "plot_w": 6, "plot_d": 8,
        "title": "6×8 — 1BHK Compact (48m²)",
        "rooms": [
            {"label": "Living Room",  "p1": {"x": 0,   "y": 0}, "p2": {"x": 3.5, "y": 3.5}, "metadata": {"type": "living"}},
            {"label": "Kitchen",      "p1": {"x": 3.5, "y": 0}, "p2": {"x": 6,   "y": 3.5}, "metadata": {"type": "kitchen"}},
            {"label": "Bedroom",      "p1": {"x": 0,   "y": 3.5},"p2": {"x": 4,  "y": 8},   "metadata": {"type": "bedroom"}},
            {"label": "Bathroom",     "p1": {"x": 4,   "y": 3.5},"p2": {"x": 6,  "y": 8},   "metadata": {"type": "bathroom"}},
        ]
    },
    # ─────────────────────────  12×10 — 3BHK Luxury  ─────────────────────────
    {
        "style": "luxury", "bedrooms": 3, "bathrooms": 3, "plot_w": 12, "plot_d": 10,
        "title": "12×10 — 3BHK Luxury (120m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 7,  "y": 4},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 7,   "y": 0},  "p2": {"x": 12, "y": 4},  "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 4},  "p2": {"x": 4.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4.5, "y": 4},  "p2": {"x": 6,  "y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6,   "y": 4},  "p2": {"x": 9.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 9.5, "y": 4},  "p2": {"x": 12, "y": 7},  "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 9.5, "y": 7},  "p2": {"x": 12, "y": 10}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  8×10 — 2BHK with Balcony  ───────────────────
    {
        "style": "modern", "bedrooms": 2, "bathrooms": 2, "plot_w": 8, "plot_d": 10,
        "title": "8×10 — 2BHK + Balcony (80m²)",
        "rooms": [
            {"label": "Balcony",        "p1": {"x": 0,   "y": 0},  "p2": {"x": 2,  "y": 4},  "metadata": {"type": "balcony"}},
            {"label": "Living Room",    "p1": {"x": 2,   "y": 0},  "p2": {"x": 6,  "y": 4},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 6,   "y": 0},  "p2": {"x": 8,  "y": 4},  "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 4},  "p2": {"x": 4.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4.5, "y": 4},  "p2": {"x": 6,  "y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6,   "y": 4},  "p2": {"x": 8,  "y": 10}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  9×11 — 2BHK Vastu  ───────────────────────────
    {
        "style": "traditional", "bedrooms": 2, "bathrooms": 2, "plot_w": 9, "plot_d": 11,
        "title": "9×11 — 2BHK Vastu (99m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 5,  "y": 4.5},"metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 5,   "y": 0},  "p2": {"x": 9,  "y": 4.5},"metadata": {"type": "kitchen"}},
            {"label": "Pooja Room",     "p1": {"x": 0,   "y": 4.5},"p2": {"x": 2.5,"y": 6.5},"metadata": {"type": "pooja"}},
            {"label": "Corridor",       "p1": {"x": 2.5, "y": 4.5},"p2": {"x": 9,  "y": 6.5},"metadata": {"type": "corridor"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 6.5},"p2": {"x": 5,  "y": 11}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 5,   "y": 6.5},"p2": {"x": 6.5,"y": 11}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6.5, "y": 6.5},"p2": {"x": 9,  "y": 11}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  15×10 — 4BHK Luxury  ─────────────────────────
    {
        "style": "luxury", "bedrooms": 4, "bathrooms": 4, "plot_w": 15, "plot_d": 10,
        "title": "15×10 — 4BHK Luxury (150m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 8,  "y": 4},  "metadata": {"type": "living"}},
            {"label": "Dining Room",    "p1": {"x": 8,   "y": 0},  "p2": {"x": 11, "y": 4},  "metadata": {"type": "dining"}},
            {"label": "Kitchen",        "p1": {"x": 11,  "y": 0},  "p2": {"x": 15, "y": 4},  "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 4},  "p2": {"x": 4.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4.5, "y": 4},  "p2": {"x": 6,  "y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6,   "y": 4},  "p2": {"x": 9.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 9.5, "y": 4},  "p2": {"x": 11, "y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 11,  "y": 4},  "p2": {"x": 13.5,"y":10}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 3",         "p1": {"x": 13.5,"y": 4},  "p2": {"x": 15, "y": 7},  "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 4",      "p1": {"x": 13.5,"y": 7},  "p2": {"x": 15, "y": 10}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  8×12 — 3BHK with Study  ─────────────────────
    {
        "style": "modern", "bedrooms": 3, "bathrooms": 2, "plot_w": 8, "plot_d": 12,
        "title": "8×12 — 3BHK + Study (96m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 4.5,"y": 5},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 4.5, "y": 0},  "p2": {"x": 8,  "y": 5},  "metadata": {"type": "kitchen"}},
            {"label": "Study Room",     "p1": {"x": 0,   "y": 5},  "p2": {"x": 2.5,"y": 7},  "metadata": {"type": "study"}},
            {"label": "Corridor",       "p1": {"x": 2.5, "y": 5},  "p2": {"x": 8,  "y": 7},  "metadata": {"type": "corridor"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 7},  "p2": {"x": 4,  "y": 12}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4,   "y": 7},  "p2": {"x": 5.5,"y": 12}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 5.5, "y": 7},  "p2": {"x": 8,  "y": 9.5},"metadata": {"type": "bedroom"}},
            {"label": "Bathroom",       "p1": {"x": 5.5, "y": 9.5},"p2": {"x": 8,  "y": 12}, "metadata": {"type": "bathroom"}},
        ]
    },
    # ─────────────────────────  10×8 — 2BHK Open Kitchen  ───────────────────
    {
        "style": "modern", "bedrooms": 2, "bathrooms": 2, "plot_w": 10, "plot_d": 8,
        "title": "10×8 — 2BHK Open Kitchen (80m²)",
        "rooms": [
            {"label": "Living & Kitchen","p1": {"x": 0,  "y": 0},  "p2": {"x": 10, "y": 3.5},"metadata": {"type": "living"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 3.5},"p2": {"x": 5.5,"y": 8},  "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 5.5, "y": 3.5},"p2": {"x": 7.5,"y": 8},  "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 7.5, "y": 3.5},"p2": {"x": 10, "y": 8},  "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  8×10 — 3BHK Compact  ────────────────────────
    {
        "style": "minimalist", "bedrooms": 3, "bathrooms": 2, "plot_w": 8, "plot_d": 10,
        "title": "8×10 — 3BHK Compact (80m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 4.5,"y": 4},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 4.5, "y": 0},  "p2": {"x": 8,  "y": 4},  "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 4},  "p2": {"x": 3.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 3.5, "y": 4},  "p2": {"x": 5,  "y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 5,   "y": 4},  "p2": {"x": 8,  "y": 7},  "metadata": {"type": "bedroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 5,   "y": 7},  "p2": {"x": 8,  "y": 10}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  12×14 — 4BHK Vastu  ──────────────────────────
    {
        "style": "traditional", "bedrooms": 4, "bathrooms": 3, "plot_w": 12, "plot_d": 14,
        "title": "12×14 — 4BHK Vastu (168m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 7,  "y": 5},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 7,   "y": 0},  "p2": {"x": 12, "y": 5},  "metadata": {"type": "kitchen"}},
            {"label": "Pooja Room",     "p1": {"x": 0,   "y": 5},  "p2": {"x": 2.5,"y": 7},  "metadata": {"type": "pooja"}},
            {"label": "Dining Room",    "p1": {"x": 2.5, "y": 5},  "p2": {"x": 12, "y": 7},  "metadata": {"type": "dining"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 7},  "p2": {"x": 4,  "y": 14}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4,   "y": 7},  "p2": {"x": 5.5,"y": 14}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 5.5, "y": 7},  "p2": {"x": 8.5,"y": 14}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 8.5, "y": 7},  "p2": {"x": 10, "y": 14}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 10,  "y": 7},  "p2": {"x": 12, "y": 10.5},"metadata": {"type": "bedroom"}},
            {"label": "Bedroom 4",      "p1": {"x": 10,  "y": 10.5},"p2":{"x": 12, "y": 14}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  7×9 — 2BHK with Dining  ─────────────────────
    {
        "style": "modern", "bedrooms": 2, "bathrooms": 1, "plot_w": 7, "plot_d": 9,
        "title": "7×9 — 2BHK + Dining (63m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 4.5,"y": 3.5},"metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 4.5, "y": 0},  "p2": {"x": 7,  "y": 3.5},"metadata": {"type": "kitchen"}},
            {"label": "Dining Room",    "p1": {"x": 0,   "y": 3.5},"p2": {"x": 7,  "y": 5.5},"metadata": {"type": "dining"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 5.5},"p2": {"x": 4,  "y": 9},  "metadata": {"type": "bedroom"}},
            {"label": "Bathroom",       "p1": {"x": 4,   "y": 5.5},"p2": {"x": 5.5,"y": 9},  "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 5.5, "y": 5.5},"p2": {"x": 7,  "y": 9},  "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  10×15 — 3BHK + Servant  ─────────────────────
    {
        "style": "luxury", "bedrooms": 3, "bathrooms": 3, "plot_w": 10, "plot_d": 15,
        "title": "10×15 — 3BHK + Servant (150m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 6,  "y": 5.5},"metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 6,   "y": 0},  "p2": {"x": 10, "y": 5.5},"metadata": {"type": "kitchen"}},
            {"label": "Corridor",       "p1": {"x": 0,   "y": 5.5},"p2": {"x": 10, "y": 7},  "metadata": {"type": "corridor"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 7},  "p2": {"x": 4.5,"y": 15}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4.5, "y": 7},  "p2": {"x": 6,  "y": 15}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6,   "y": 7},  "p2": {"x": 8.5,"y": 12}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 8.5, "y": 7},  "p2": {"x": 10, "y": 12}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 6,   "y": 12}, "p2": {"x": 8.5,"y": 15}, "metadata": {"type": "bedroom"}},
            {"label": "Servant Room",   "p1": {"x": 8.5, "y": 12}, "p2": {"x": 10, "y": 15}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  6×10 — 1BHK + Study  ────────────────────────
    {
        "style": "minimalist", "bedrooms": 1, "bathrooms": 1, "plot_w": 6, "plot_d": 10,
        "title": "6×10 — 1BHK + Study (60m²)",
        "rooms": [
            {"label": "Living Room",  "p1": {"x": 0,   "y": 0},  "p2": {"x": 3.5,"y": 4},  "metadata": {"type": "living"}},
            {"label": "Kitchen",      "p1": {"x": 3.5, "y": 0},  "p2": {"x": 6,  "y": 4},  "metadata": {"type": "kitchen"}},
            {"label": "Study Room",   "p1": {"x": 0,   "y": 4},  "p2": {"x": 2.5,"y": 6},  "metadata": {"type": "study"}},
            {"label": "Bathroom",     "p1": {"x": 2.5, "y": 4},  "p2": {"x": 6,  "y": 6},  "metadata": {"type": "bathroom"}},
            {"label": "Bedroom",      "p1": {"x": 0,   "y": 6},  "p2": {"x": 6,  "y": 10}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  12×12 — 3BHK Square  ─────────────────────────
    {
        "style": "modern", "bedrooms": 3, "bathrooms": 3, "plot_w": 12, "plot_d": 12,
        "title": "12×12 — 3BHK Square (144m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 7,  "y": 5},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 7,   "y": 0},  "p2": {"x": 12, "y": 5},  "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 5},  "p2": {"x": 4.5,"y": 12}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4.5, "y": 5},  "p2": {"x": 6,  "y": 12}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6,   "y": 5},  "p2": {"x": 9.5,"y": 12}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 9.5, "y": 5},  "p2": {"x": 12, "y": 8.5},"metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 9.5, "y": 8.5},"p2": {"x": 12, "y": 12}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  8×8 — 2BHK Compact  ─────────────────────────
    {
        "style": "minimalist", "bedrooms": 2, "bathrooms": 1, "plot_w": 8, "plot_d": 8,
        "title": "8×8 — 2BHK Compact (64m²)",
        "rooms": [
            {"label": "Living Room",  "p1": {"x": 0,   "y": 0},  "p2": {"x": 4.5,"y": 3.5},"metadata": {"type": "living"}},
            {"label": "Kitchen",      "p1": {"x": 4.5, "y": 0},  "p2": {"x": 8,  "y": 3.5},"metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom","p1": {"x": 0,  "y": 3.5},"p2": {"x": 4.5,"y": 8},  "metadata": {"type": "bedroom"}},
            {"label": "Bathroom",     "p1": {"x": 4.5, "y": 3.5},"p2": {"x": 6,  "y": 8},  "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",    "p1": {"x": 6,   "y": 3.5},"p2": {"x": 8,  "y": 8},  "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  14×10 — 4BHK Modern  ─────────────────────────
    {
        "style": "modern", "bedrooms": 4, "bathrooms": 3, "plot_w": 14, "plot_d": 10,
        "title": "14×10 — 4BHK Modern (140m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 8,  "y": 4},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 8,   "y": 0},  "p2": {"x": 14, "y": 4},  "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 4},  "p2": {"x": 4.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4.5, "y": 4},  "p2": {"x": 6,  "y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6,   "y": 4},  "p2": {"x": 9.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Bath 2",         "p1": {"x": 9.5, "y": 4},  "p2": {"x": 11, "y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 11,  "y": 4},  "p2": {"x": 14, "y": 7},  "metadata": {"type": "bedroom"}},
            {"label": "Bedroom 4",      "p1": {"x": 11,  "y": 7},  "p2": {"x": 14, "y": 10}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  8×12 — 2BHK + Pooja + Parking  ──────────────
    {
        "style": "traditional", "bedrooms": 2, "bathrooms": 2, "plot_w": 8, "plot_d": 12,
        "title": "8×12 — 2BHK Vastu + Pooja (96m²)",
        "rooms": [
            {"label": "Parking",        "p1": {"x": 0,   "y": 0},  "p2": {"x": 8,  "y": 2.5},"metadata": {"type": "garage"}},
            {"label": "Living Room",    "p1": {"x": 0,   "y": 2.5},"p2": {"x": 4.5,"y": 6},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 4.5, "y": 2.5},"p2": {"x": 8,  "y": 6},  "metadata": {"type": "kitchen"}},
            {"label": "Pooja Room",     "p1": {"x": 0,   "y": 6},  "p2": {"x": 2,  "y": 7.5},"metadata": {"type": "pooja"}},
            {"label": "Corridor",       "p1": {"x": 2,   "y": 6},  "p2": {"x": 8,  "y": 7.5},"metadata": {"type": "corridor"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 7.5},"p2": {"x": 4.5,"y": 12}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4.5, "y": 7.5},"p2": {"x": 6,  "y": 12}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 6,   "y": 7.5},"p2": {"x": 8,  "y": 12}, "metadata": {"type": "bedroom"}},
        ]
    },
    # ─────────────────────────  10×10 — 3BHK Balanced  ───────────────────────
    {
        "style": "modern", "bedrooms": 3, "bathrooms": 2, "plot_w": 10, "plot_d": 10,
        "title": "10×10 — 3BHK Balanced (100m²)",
        "rooms": [
            {"label": "Living Room",    "p1": {"x": 0,   "y": 0},  "p2": {"x": 5.5,"y": 4},  "metadata": {"type": "living"}},
            {"label": "Kitchen",        "p1": {"x": 5.5, "y": 0},  "p2": {"x": 10, "y": 4},  "metadata": {"type": "kitchen"}},
            {"label": "Master Bedroom", "p1": {"x": 0,   "y": 4},  "p2": {"x": 4,  "y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Master Bath",    "p1": {"x": 4,   "y": 4},  "p2": {"x": 5.5,"y": 10}, "metadata": {"type": "bathroom"}},
            {"label": "Bedroom 2",      "p1": {"x": 5.5, "y": 4},  "p2": {"x": 7.5,"y": 10}, "metadata": {"type": "bedroom"}},
            {"label": "Bathroom",       "p1": {"x": 7.5, "y": 4},  "p2": {"x": 10, "y": 6.5},"metadata": {"type": "bathroom"}},
            {"label": "Bedroom 3",      "p1": {"x": 7.5, "y": 6.5},"p2": {"x": 10, "y": 10}, "metadata": {"type": "bedroom"}},
        ]
    },
]


async def main():
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("❌ MONGODB_URI not set in .env")
        return

    client = AsyncIOMotorClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=10000)
    db = client["gplan"]

    # Clear old seed plans
    await db["seed_plans"].delete_many({})
    print("🗑️  Cleared old seed plans")

    # Insert new plans
    docs = []
    for p in PLANS:
        docs.append({
            "style":     p["style"],
            "bedrooms":  p["bedrooms"],
            "bathrooms": p["bathrooms"],
            "plot_w":    p["plot_w"],
            "plot_d":    p["plot_d"],
            "title":     p["title"],
            "rooms":     p["rooms"],
        })

    result = await db["seed_plans"].insert_many(docs)
    print(f"✅ Inserted {len(result.inserted_ids)} seed plans into MongoDB!")

    # Create indexes
    await db["seed_plans"].create_index("style")
    await db["seed_plans"].create_index([("bedrooms", 1), ("style", 1)])
    print("✅ Indexes created on style, bedrooms")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
