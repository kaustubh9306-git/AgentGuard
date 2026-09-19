from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import boto3
import json

app = FastAPI(title="AgentGuard API", version="1.0")

# Enable CORS so your frontend (index.html) can communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class OrderRequest(BaseModel):
    product_id: int
    product_name: str
    price: float
    delivery_days: int
    max_budget: float

@app.post("/agentguard/ai-shop")
def ai_shop(req: PromptRequest):
    """Processes user prompt intent, extracts constraints, and returns candidate options."""
    prompt_lower = req.prompt.lower()
    
    # Smart intent & product mapping based on prompt keywords
    if "tablet" in prompt_lower:
        category = "Tablet"
        max_price = 40000
        products = [
            {"id": 1, "name": "Samsung Galaxy Tab S9", "price": 38999, "delivery_days": 2},
            {"id": 2, "name": "Apple iPad Air (256GB)", "price": 44999, "delivery_days": 3}, # Slightly over budget to test firewall block
            {"id": 3, "name": "Lenovo Tab P12", "price": 32999, "delivery_days": 4}
        ]
    elif "laptop" in prompt_lower:
        category = "Laptop"
        max_price = 70000
        products = [
            {"id": 4, "name": "Lenovo IdeaPad Slim 5 (16GB)", "price": 64999, "delivery_days": 2},
            {"id": 5, "name": "ASUS Vivobook Pro 15", "price": 72000, "delivery_days": 5}, # Over budget
            {"id": 6, "name": "MacBook Air M1", "price": 74999, "delivery_days": 1}      # Over budget
        ]
    elif "earbuds" in prompt_lower or "earphone" in prompt_lower:
        category = "Audio"
        max_price = 5000
        products = [
            {"id": 7, "name": "OnePlus Buds Z2", "price": 3999, "delivery_days": 1},
            {"id": 8, "name": "Realme Buds Air 5", "price": 3499, "delivery_days": 2},
            {"id": 9, "name": "Sony WF-C500", "price": 5999, "delivery_days": 3}      # Over budget
        ]
    else:
        category = "Electronics"
        max_price = 75000
        products = [
            {"id": 10, "name": "Generic Flagship Smartphone", "price": 69999, "delivery_days": 2},
            {"id": 11, "name": "Ultra Smartphone Pro", "price": 79999, "delivery_days": 3},
            {"id": 12, "name": "Budget Smartphone Lite", "price": 24999, "delivery_days": 1}
        ]

    # Evaluate each product against the hard budget constraint
    recommendations = []
    for product in products:
        is_approved = product["price"] <= max_price
        verdict = "APPROVE" if is_approved else "BLOCK"
        
        pros = [f"Within budget (₹{product['price']:,})" if is_approved else "Exceeds maximum budget limit"]
        if product["delivery_days"] <= 3:
            pros.append(f"Fast delivery ({product['delivery_days']} days)")
            
        cons = [] if is_approved else [f"Price ₹{product['price']:,} is higher than limit ₹{max_price:,}"]

        recommendations.append({
            **product,
            "security_verdict": verdict,
            "pros": pros,
            "cons": cons
        })
        
    return {
        "user_intent": {
            "category": category,
            "hard_constraints": {
                "max_price": max_price
            }
        },
        "recommendations": recommendations
    }

from datetime import datetime

@app.post("/agentguard/submit-order")
def submit_order(order: OrderRequest):
    """Executes secure order validation and logs the transaction persistently."""
    if order.price > order.max_budget:
        raise HTTPException(status_code=403, detail="Order blocked: Price exceeds user budget constraint.")
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": "Order Execution",
        "detail": f"Successfully purchased {order.product_name} for ₹{order.price:,}",
        "verdict": "APPROVE"
    }
    
    log_file = "audit_logs.json"
    logs = []
    
    # Read existing logs if file exists
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                content = f.read()
                if content.strip():
                    logs = json.loads(content)
        except Exception:
            logs = []
            
    logs.append(log_entry)
    
    # Write back to audit_logs.json
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)
        
    return {"status": "success", "message": f"Order for {order.product_name} secured and executed successfully!"}

@app.get("/agentguard/audit-logs")
def get_audit_logs(limit: int = Query(50, description="Max logs to return")):
    """Returns persistent audit logs from audit_logs.json, supporting both list and object formats."""
    log_file = "audit_logs.json"
    if not os.path.exists(log_file):
        # Return a default initial log if none exists yet so UI has something to show
        return [{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "System Initialized",
            "detail": "AgentGuard security engine active and monitoring.",
            "verdict": "APPROVE"
        }]
    
    try:
        with open(log_file, "r") as f:
            data = json.load(f)
            # Handle if data is stored as a list or a dict wrapper
            logs = data.get("logs", data) if isinstance(data, dict) else data
            if not isinstance(logs, list):
                logs = []
            return logs[::-1][:limit]
    except Exception:
        return []

    # Fallback alias route without prefix in case the frontend calls /audit-logs directly
@app.get("/audit-logs")
def get_audit_logs_alias(limit: int = Query(50)):
    return get_audit_logs(limit=limit)