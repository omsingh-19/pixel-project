from .database import SessionLocal
from . import models

PRODUCTS = [
    {"name": "Biscuits", "category": "Snacks", "base_price": 20, "tags": "tea,snack,kids", "seasonal": "all"},
    {"name": "Tea", "category": "Beverages", "base_price": 30, "tags": "hot,morning,daily", "seasonal": "rainy,winter,all"},
    {"name": "Coffee", "category": "Beverages", "base_price": 80, "tags": "premium,office,morning", "seasonal": "winter,all"},
    {"name": "Milk", "category": "Dairy", "base_price": 28, "tags": "breakfast,daily,family", "seasonal": "all"},
    {"name": "Bread", "category": "Bakery", "base_price": 35, "tags": "breakfast,family,quick", "seasonal": "all"},
    {"name": "Jam", "category": "Bakery", "base_price": 65, "tags": "breakfast,sweet,family", "seasonal": "all"},
    {"name": "Butter", "category": "Dairy", "base_price": 55, "tags": "breakfast,premium,family", "seasonal": "all"},
    {"name": "Namkeen", "category": "Snacks", "base_price": 25, "tags": "snack,evening,spicy", "seasonal": "all"},
    {"name": "Chips", "category": "Snacks", "base_price": 20, "tags": "snack,kids,party", "seasonal": "all"},
    {"name": "Cold Drink", "category": "Beverages", "base_price": 40, "tags": "summer,party,chill", "seasonal": "summer,all"},
    {"name": "Juice", "category": "Beverages", "base_price": 35, "tags": "kids,healthy,refreshing", "seasonal": "summer,all"},
    {"name": "Instant Noodles", "category": "Ready-to-Eat", "base_price": 18, "tags": "quick,students,evening", "seasonal": "rainy,all"},
    {"name": "Sugar", "category": "Grocery", "base_price": 45, "tags": "tea,daily,family", "seasonal": "all"},
    {"name": "Soap", "category": "Personal Care", "base_price": 32, "tags": "daily,hygiene,family", "seasonal": "all"},
    {"name": "Shampoo", "category": "Personal Care", "base_price": 60, "tags": "hygiene,premium,family", "seasonal": "all"},
    {"name": "Detergent", "category": "Home Care", "base_price": 90, "tags": "home,daily,family", "seasonal": "all"},
    {"name": "Chocolate", "category": "Snacks", "base_price": 15, "tags": "kids,gift,impulse", "seasonal": "all"},
    {"name": "Ice Cream", "category": "Dessert", "base_price": 50, "tags": "summer,kids,treat", "seasonal": "summer"},
    {"name": "Umbrella", "category": "Utility", "base_price": 180, "tags": "rainy,utility,seasonal", "seasonal": "rainy"},
    {"name": "Soup Pack", "category": "Ready-to-Eat", "base_price": 45, "tags": "winter,comfort,quick", "seasonal": "winter,rainy"},
    {"name": "Dry Fruits", "category": "Premium Grocery", "base_price": 220, "tags": "premium,healthy,gift", "seasonal": "festival,all"},
]


def seed_products():
    db = SessionLocal()
    try:
        if db.query(models.Product).count() > 0:
            return
        for item in PRODUCTS:
            db.add(models.Product(**item))
        db.commit()
    finally:
        db.close()
