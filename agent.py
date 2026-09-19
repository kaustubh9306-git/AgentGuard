import json
import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from products import products_found

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def process_user_shopping_request(user_prompt: str):
  extraction_prompt = f"""
    Analyze the following user shopping request and extract constraints into JSON format.
    Request: "{user_prompt}"
    
    Extract these fields:
    - category (string, e.g., "phone", "laptop", "monitor", "headphone", "smartwatch")
    - max_price (integer, numeric value only)
    - min_storage_gb (integer or null)
    - max_delivery_days (integer or null)
    - preferred_brand (string or null)
    
    Return ONLY valid JSON.
    """

  models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
  response_text = None

  for model_name in models_to_try:
    try:
      response = client.models.generate_content(
          model=model_name,
          contents=extraction_prompt,
          config=types.GenerateContentConfig(response_mime_type="application/json"),
      )
      if response and response.text:
        response_text = response.text
        break
    except Exception:
      continue

  intent = {}
  if response_text:
    try:
      intent = json.loads(response_text)
    except json.JSONDecodeError:
      intent = {}

  # Smart Fallback Parser
  prompt_lower = user_prompt.lower()
  detected_category = intent.get("category", "").lower()

  if (
      not detected_category
      or detected_category not in "phone laptop monitor headphone smartwatch"
  ):
    if "phone" in prompt_lower or "mobile" in prompt_lower:
      detected_category = "phone"
    elif "laptop" in prompt_lower:
      detected_category = "laptop"
    elif "monitor" in prompt_lower or "display" in prompt_lower:
      detected_category = "monitor"
    elif "headphone" in prompt_lower or "earbud" in prompt_lower:
      detected_category = "headphone"
    elif "watch" in prompt_lower:
      detected_category = "smartwatch"
    else:
      detected_category = "phone"

  intent["category"] = detected_category

  if not intent.get("max_price"):
    numbers = re.findall(r"\d+", user_prompt)
    valid_prices = [int(n) for n in numbers if int(n) > 1000]
    intent["max_price"] = (
        valid_prices[0]
        if valid_prices
        else (int(numbers[0]) if numbers else 50000)
    )

  max_budget = intent.get("max_price", 999999)

  # Filter matching products from the catalog flexibly
  matched_products = [
      p
      for p in products_found
      if detected_category in p["category"].lower()
      and p["price"] <= max_budget
  ]

  # If exact category match yields nothing, search globally by budget
  if not matched_products:
    matched_products = [p for p in products_found if p["price"] <= max_budget]

  # Sort by price ascending to give best options first
  matched_products.sort(key=lambda x: (x["delivery_days"], x["price"]))

  # Grab top 3 options to fulfill the multi-option requirement!
  top_proposals = (
      matched_products[:3] if matched_products else products_found[:3]
  )

  return {
      "user_intent": {
          "hard_constraints": {
              "max_price": max_budget,
              "min_storage_gb": intent.get("min_storage_gb"),
              "max_delivery_days": intent.get("max_delivery_days"),
          }
      },
      "proposed_products": top_proposals,
  }