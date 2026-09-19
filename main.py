from datetime import datetime
import json
import os
from agent import process_user_shopping_request
from fastapi import FastAPI, HTTPException
from guard import validate_purchase
from pydantic import BaseModel

app = FastAPI(
    title="AgentGuard Multi-Option Security & Recommendation Engine",
    version="1.0",
)

AUDIT_LOG_FILE = "audit_logs.json"


def write_to_audit_log(entry: dict):
  logs = []
  if os.path.exists(AUDIT_LOG_FILE):
    try:
      with open(AUDIT_LOG_FILE, "r") as f:
        logs = json.load(f)
    except json.JSONDecodeError:
      logs = []
  logs.append(entry)
  with open(AUDIT_LOG_FILE, "w") as f:
    json.dump(logs, f, indent=2)


class NaturalLanguageRequest(BaseModel):
  agent_id: str = "gemini_shopping_bot"
  user_prompt: str


@app.get("/")
def read_root():
  return {"message": "AgentGuard Engine is online and ready."}


@app.post("/agentguard/ai-shop")
def ai_shopping_workflow(payload: NaturalLanguageRequest):
  agent_output = process_user_shopping_request(payload.user_prompt)

  user_intent = agent_output["user_intent"]
  proposed_products = agent_output["proposed_products"]
  constraints = user_intent.get("constraints", user_intent.get("hard_constraints", {}))
  max_price = constraints.get("max_price")

  evaluated_options = []

  for product in proposed_products:
    evaluation = validate_purchase(user_intent, product)

    pros = []
    cons = []

    # Safe Budget evaluation messaging
    if evaluation["checks"]["budget"]["status"] == "PASS":
      pros.append(f"Fits within budget (₹{product['price']})")
    else:
      if max_price is not None:
        cons.append(f"Exceeds max budget of ₹{max_price}")
      else:
        cons.append("Does not meet budget constraints")

    # Safe Storage evaluation messaging
    if evaluation["checks"]["storage"]["status"] == "PASS":
      pros.append(f"Meets storage requirement")
    else:
      cons.append(f"Storage size is below requirement")

    # Safe Delivery evaluation messaging
    if evaluation["checks"]["delivery"]["status"] == "PASS":
      pros.append(f"Fast delivery in {product['delivery_days']} day(s)")
    else:
      cons.append(f"Delivery takes too long")

    evaluated_options.append({
        "product": product,
        "guard_decision": evaluation["decision"],
        "reason": evaluation["reason"],
        "pros": pros,
        "cons": cons,
        "checks": evaluation["checks"],
    })

  log_entry = {
      "timestamp": datetime.utcnow().isoformat(),
      "agent_id": payload.agent_id,
      "evaluation_type": "multi_option_ai_workflow",
      "user_prompt": payload.user_prompt,
      "extracted_intent": user_intent,
      "options_evaluated": len(evaluated_options),
  }
  write_to_audit_log(log_entry)

  return {
      "agent_natural_language_request": payload.user_prompt,
      "gemini_extracted_intent": user_intent,
      "recommendation_engine_options": evaluated_options,
  }