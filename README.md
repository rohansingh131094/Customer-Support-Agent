# Bookly Support Agent

A conversational AI customer support agent for Bookly, a fictional online bookstore. Built with Python, FastAPI, and the Anthropic Claude API.

## What it does

- **Order status** — look up real-time order information by order ID
- **Returns & refunds** — multi-turn flow that collects context and confirms before acting
- **Policy questions** — shipping, returns, password reset, payment via tool-backed lookup

## Architecture

```
User (browser)
     │  HTTP
     ▼
FastAPI  (/chat endpoint)
     │
     ▼
Agent Loop  (agent/loop.py)
  ├── System prompt  (agent/system_prompt.py)
  ├── Tool definitions  (agent/tools.py)
  └── Anthropic Claude API
          │  tool_use
          ▼
     Tool execution
       ├── send_otp          →  data/auth.py
       ├── verify_otp        →  data/auth.py
       ├── get_order_status  →  data/orders.py
       ├── initiate_return   →  data/orders.py
       └── get_policy        →  data/policies.json
```

Session history is stored in-memory, keyed by a per-browser UUID.

## Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd bookly-agent

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# Edit .env and add your Anthropic API key
```

## Run

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Test scenarios

**Authentication is required for all order and return flows.** Use any 6-digit code to verify.

| Email | Phone | Name | Orders |
|---|---|---|---|
| sarah@gmail.com | 555-0201 | Sarah Chen | BK-2001 (delivered), BK-2002 (delayed) |
| john@gmail.com | 555-0301 | John Doe | BK-3001 (shipped), BK-3002 (delivered) |

| Scenario | How to trigger |
|---|---|
| Return flow | Authenticate as Sarah or John → "I want to return my order" |
| Delayed order | Authenticate as Sarah → ask about orders |
| Shipped order | Authenticate as John → ask about orders |
| Policy question | `"How long does shipping take?"` — no auth needed |
| Policy question | `"How long does shipping take?"` — no auth needed |
| Escalation friction | `"I want to speak to a human"` → agent tries to help first |
| Out-of-scope | `"What's the weather like?"` |

## Project structure

```
.
├── main.py                 # FastAPI app + /chat endpoint
├── agent/
│   ├── loop.py             # Agent loop — tool-use orchestration
│   ├── tools.py            # Tool definitions + execution
│   ├── sessions.py         # In-memory session/history management
│   └── system_prompt.py    # System prompt
├── data/
│   ├── orders.py           # Mock order database + return logic
│   ├── policies.py         # Policy loader
│   └── policies.json       # Policy content
├── static/
│   └── index.html          # Chat UI
├── requirements.txt
└── .env.example
```
