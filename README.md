# AgentGuard 🛡️
> Pre-Execution Security & Guardrail Engine for Autonomous Shopping Agents

AgentGuard is a middleware firewall designed to intercept, evaluate, and sandbox actions taken by autonomous AI shopping agents. Before any financial transaction or order is executed, AgentGuard verifies product options against user-defined hard constraints (such as strict budget caps, specifications, and delivery thresholds) and screens prompts for prompt injection vulnerabilities.

---

## 🚀 Key Features
- **Pre-Execution Validation:** Independently evaluates candidate products against hard constraints before checkout.
- **Intent & Constraint Parsing:** Extracts user intent and parameters (like max budget, storage, or delivery times) from natural language prompts.
- **Prompt Injection Defense:** Scans inputs for malicious prompt manipulation before execution.
- **Fail-Closed Security Model:** Automatically blocks transactions that violate security policies or fail validation checks.
- **Persistent Audit Logging:** Maintains a full audit trail of all evaluations, approvals, and blocks.

---

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Frontend:** HTML5, Tailwind CSS, JavaScript (Vanilla)
- **Containerization:** Docker

---

## 📁 Project Structure
```text
AgentGuard/
│
├── main.py            # FastAPI entrypoint & main server routes
├── guard.py           # Security checks & prompt injection scanning
├── agent.py           # Agent logic and orchestration
├── products.py        # Product candidate evaluation logic
├── orders.py          # Secure order execution handler
├── tools.py           # Helper utilities and tools
├── audit.py           # Audit logging mechanism
├── Dockerfile         # Docker configuration file
├── requirements.txt   # Python dependencies
└── index.html         # Frontend user interface
