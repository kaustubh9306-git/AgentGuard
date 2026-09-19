# agent.py

def process_user_shopping_request(prompt: str):
    """Parses prompt intent and returns candidate products for evaluation."""
    prompt_lower = prompt.lower()
    
    # Default intent
    category = "Electronics"
    max_price = 75000
    
    # Simple keyword detection to adjust intent based on prompt
    if "tablet" in prompt_lower:
        category = "Tablet"
        max_price = 40000
        products = [
            {"id": 1, "name": "Samsung Galaxy Tab S9", "price": 38999, "delivery_days": 2},
            {"id": 2, "name": "Apple iPad Air (256GB)", "price": 54999, "delivery_days": 3},
            {"id": 3, "name": "Lenovo Tab P12", "price": 32999, "delivery_days": 4}
        ]
    elif "laptop" in prompt_lower:
        category = "Laptop"
        max_price = 70000
        products = [
            {"id": 4, "name": "Lenovo IdeaPad Slim 5 (16GB)", "price": 64999, "delivery_days": 2},
            {"id": 5, "name": "ASUS Vivobook Pro 15", "price": 72000, "delivery_days": 5},
            {"id": 6, "name": "MacBook Air M1", "price": 74999, "delivery_days": 1}
        ]
    elif "earbuds" in prompt_lower or "earphone" in prompt_lower:
        category = "Audio"
        max_price = 5000
        products = [
            {"id": 7, "name": "OnePlus Buds Z2", "price": 3999, "delivery_days": 1},
            {"id": 8, "name": "Realme Buds Air 5", "price": 3499, "delivery_days": 2},
            {"id": 9, "name": "Sony WF-C500", "price": 5999, "delivery_days": 3}
        ]
    else:
        # Default fallback products
        products = [
            {"id": 10, "name": "Generic Flagship Smartphone", "price": 69999, "delivery_days": 2},
            {"id": 11, "name": "Ultra Smartphone Pro", "price": 79999, "delivery_days": 3},
            {"id": 12, "name": "Budget Smartphone Lite", "price": 24999, "delivery_days": 1}
        ]

    return {
        "user_intent": {
            "category": category,
            "hard_constraints": {
                "max_price": max_price
            }
        },
        "proposed_products": products
    }