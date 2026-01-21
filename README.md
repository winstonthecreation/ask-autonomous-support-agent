# ASK — Assured Safe Kernel for Autonomous Support Agents

ASK is a prototype system for building autonomous AI support agents that can be trained and constrained using human-readable business rules.

It is designed to explore a core problem faced by companies like Minimal AI:
"how to make autonomous agents safe, self-serve, and adaptable to real-world systems."

---

## Motivation

Autonomous AI agents often fail in production because:

- They act too eagerly (refund too early, cancel incorrectly)
- They rely on fragile prompt tuning
- They require engineers to configure every integration

ASK explores a different approach:
"treat AI like a human employee that must follow explicit rules."

---

## Core Idea

Instead of trusting an LLM directly, ASK inserts a formal rule layer between the AI and the real world.

The system follows this loop:

**propose → enforce → act → observe → retry**

1. The LLM proposes a plan
2. ASK checks the plan against human-defined rules
3. Illegal actions are blocked
4. The agent retries with a better plan
5. Legal actions execute using tools
6. The world state is observed and the loop continues

---

## High-Level Architecture

- **Support Agent**
  - Uses an LLM to propose action plans

- **ASK (Assured Safe Kernel)**
  - Enforces business rules
  - Blocks unsafe actions
  - Allows safe retries

- **Tools / APIs (mocked)**
  - `check_inventory`
  - `refund_order`
  - `verify_order`

- **World State**
  - Tracks inventory, refund status, and observations

This architecture is intentionally designed to support a future **AI Manager** layer that can train, monitor, and improve agents over time.

---

## Example: Non-Technical Training

A store owner gives feedback:

> “Don’t refund if inventory is available.”

ASK translates this into a formal rule:

LAW {
when inventory > 0
block refund_order
because "Check inventory first"
}

This allows non-technical users to shape agent behavior without prompts or parameters.

---

## Demo video (15s):
Short terminal run showing ASK blocking an unsafe refund and allowing a correct retry:
https://youtu.be/1nBbnCSz40M

file to run: `step1_test_llm.py`

## Expected behavior

**First attempt**
- Agent tries to refund immediately
- ASK blocks the action

**Second attempt**
- Agent checks inventory
- Refund succeeds

This demonstrates **autonomous retries under explicit constraints**.

---

## Current Limitations

This is a prototype, not a production system.

- APIs are mocked (not real Shopify / ERP endpoints)
- LLM JSON parsing is still fragile
- Rule language is intentionally simple

---

## Future Directions

- Bulletproof LLM parsing and schema handling
- Real HTTP-based integrations (Shopify / ERP / legacy systems)
- Richer rule language, including:
  - Time-based constraints
  - Customer risk flags
  - Approval workflows
- AI Manager layer for training and monitoring agents

---

## Why This Matters

ASK is a step toward:

- AI that can be trained like a human
- AI that is constrained like software
- AI that can safely operate in messy, real-world systems


