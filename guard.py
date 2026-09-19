def validate_purchase(user_intent: dict, product: dict) -> dict:
  constraints = user_intent.get("hard_constraints", {})
  max_price = constraints.get("max_price")
  min_storage = constraints.get("min_storage_gb")
  max_delivery = constraints.get("max_delivery_days")

  checks = {}
  failed_checks = []

  # 1. Budget Check
  if max_price is not None:
    actual_price = product.get("price", 0)
    budget_pass = actual_price <= max_price
    checks["budget"] = {
        "status": "PASS" if budget_pass else "FAIL",
        "required": f"<= {max_price}",
        "actual": actual_price,
    }
    if not budget_pass:
      failed_checks.append("budget")
  else:
    checks["budget"] = {"status": "PASS", "required": "None", "actual": "N/A"}

  # 2. Storage Check (Safely guards against None values)
  if min_storage is not None:
    actual_storage = product.get("storage_gb", 0)
    storage_pass = actual_storage >= min_storage
    checks["storage"] = {
        "status": "PASS" if storage_pass else "FAIL",
        "required": f">= {min_storage}GB",
        "actual": f"{actual_storage}GB",
    }
    if not storage_pass:
      failed_checks.append("storage")
  else:
    checks["storage"] = {
        "status": "PASS",
        "required": "Not specified",
        "actual": f"{product.get('storage_gb', 'N/A')}GB",
    }

  # 3. Delivery Check (Safely guards against None values)
  if max_delivery is not None:
    actual_delivery = product.get("delivery_days", 99)
    delivery_pass = actual_delivery <= max_delivery
    checks["delivery"] = {
        "status": "PASS" if delivery_pass else "FAIL",
        "required": f"<= {max_delivery} day(s)",
        "actual": f"{actual_delivery} day(s)",
    }
    if not delivery_pass:
      failed_checks.append("delivery")
  else:
    checks["delivery"] = {
        "status": "PASS",
        "required": "Not specified",
        "actual": f"{product.get('delivery_days', 'N/A')} day(s)",
    }

  # Final Decision
  if failed_checks:
    decision = "BLOCK"
    reason = f"Mandatory constraints violated: {', '.join(failed_checks)}"
  else:
    decision = "APPROVE"
    reason = "All active constraints satisfied successfully."

  return {"decision": decision, "reason": reason, "checks": checks}

def verify_constraints(
    price: float,
    delivery_days: int,
    max_budget: float,
    max_delivery_days: int = None,
):
  """Deterministically verifies if a product proposal violates user constraints.

  Returns a string describing the violation if any constraint fails, or None if
  all checks pass.
  """
  # Check budget constraint (None-safe)
  if max_budget is not None and price > max_budget:
    return (
        f"Price (${price:,.2f}) exceeds user maximum budget"
        f" (${max_budget:,.2f})."
    )

  # Check delivery days constraint (None-safe)
  if max_delivery_days is not None and delivery_days > max_delivery_days:
    return (
        f"Delivery time ({delivery_days} days) exceeds maximum allowed"
        f" ({max_delivery_days} days)."
    )

  return None