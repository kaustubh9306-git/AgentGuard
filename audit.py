# audit.py

import json
from datetime import datetime
import os

AUDIT_LOG_PATH = "audit_logs.json"

def log_audit_event(user_requirements, product, validation_result):
    """
    Saves a secure audit trail of the agent's proposal and AgentGuard's decision.
    """
    audit_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_requirements": user_requirements,
        "proposed_product": product,
        "decision": validation_result.get("decision"),
        "reason": validation_result.get("reason"),
        "checks": validation_result.get("checks", {})
    }

    # Load existing logs or create a new list
    logs = []
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "r") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(audit_entry)

    # Save back to file
    with open(AUDIT_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=4)

    print(f"\n📜 Audit Record Safely Saved to '{AUDIT_LOG_PATH}' with Timestamp: {audit_entry['timestamp']}")
    return audit_entry