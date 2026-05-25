from data.orders import get_orders_by_contact, initiate_return_request, initiate_exchange_request
from data.knowledge import search_knowledge as _search_knowledge
from data.auth import send_otp as _send_otp, verify_otp as _verify_otp, update_shipping_address as _update_shipping_address, update_email as _update_email

TOOL_DEFINITIONS = [
    {
        "name": "send_otp",
        "description": (
            "Send a one-time verification code to the customer's email or phone number. "
            "Contact (email or phone) is the only input needed — do not ask for name, address, or any other identifier before calling this."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact": {
                    "type": "string",
                    "description": "Customer's email address or phone number",
                }
            },
            "required": ["contact"],
        },
    },
    {
        "name": "verify_otp",
        "description": (
            "Verify the one-time code the customer provided. "
            "Returns the customer's name and order IDs on success. "
            "Only call get_order_status or initiate_return after this succeeds."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact": {
                    "type": "string",
                    "description": "The same email or phone used in send_otp",
                },
                "code": {
                    "type": "string",
                    "description": "The 6-digit code the customer entered",
                },
            },
            "required": ["contact", "code"],
        },
    },
    {
        "name": "get_orders",
        "description": (
            "Look up all orders for a verified customer using their email or phone number. "
            "Call this once after verify_otp succeeds — it returns every order in a single response. "
            "Do not call it multiple times or per order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact": {
                    "type": "string",
                    "description": "The customer's email or phone number used during verification",
                }
            },
            "required": ["contact"],
        },
    },
    {
        "name": "initiate_exchange",
        "description": (
            "Initiate an exchange for a delivered order — use this when the customer "
            "agrees to receive a replacement instead of a refund. "
            "Only call after the customer has explicitly confirmed they want an exchange."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The Bookly order ID to exchange",
                },
                "reason": {
                    "type": "string",
                    "description": "The reason for the exchange",
                },
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "initiate_return",
        "description": (
            "Initiate a return or refund request for a delivered order. "
            "Only call this after the customer has been verified with verify_otp "
            "and has explicitly confirmed they want to proceed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The Bookly order ID to return",
                },
                "reason": {
                    "type": "string",
                    "description": "The customer's reason for the return",
                },
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "update_shipping_address",
        "description": (
            "Update the shipping address on the customer's account. "
            "Only call after identity has been verified with verify_otp and the customer has confirmed the new address."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact": {
                    "type": "string",
                    "description": "The customer's email or phone used during verification",
                },
                "new_address": {
                    "type": "string",
                    "description": "The new shipping address to save on the account",
                },
            },
            "required": ["contact", "new_address"],
        },
    },
    {
        "name": "update_email",
        "description": (
            "Update the email address on the customer's account. "
            "Only call after identity has been verified with verify_otp and the customer has confirmed the new email."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "contact": {
                    "type": "string",
                    "description": "The customer's email or phone used during verification",
                },
                "new_email": {
                    "type": "string",
                    "description": "The new email address to save on the account",
                },
            },
            "required": ["contact", "new_email"],
        },
    },
    {
        "name": "search_knowledge",
        "description": (
            "Search Bookly's knowledge base to answer customer questions about policies, "
            "shipping, returns, payments, or account topics. "
            "Use this instead of answering from memory — always search first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The customer's question or topic to search for",
                }
            },
            "required": ["query"],
        },
    },
]


_TOOL_INDEX = {t["name"]: t for t in TOOL_DEFINITIONS}


def get_tools(names: list) -> list:
    return [_TOOL_INDEX[name] for name in names if name in _TOOL_INDEX]


_TOOL_MAP = {
    "send_otp":          lambda i: _send_otp(i["contact"]),
    "verify_otp":        lambda i: _verify_otp(i["contact"], i["code"]),
    "get_orders":        lambda i: get_orders_by_contact(i["contact"]),
    "initiate_exchange": lambda i: initiate_exchange_request(i["order_id"], i["reason"]),
    "initiate_return":   lambda i: initiate_return_request(i["order_id"], i["reason"]),
    "update_shipping_address": lambda i: _update_shipping_address(i["contact"], i["new_address"]),
    "update_email":            lambda i: _update_email(i["contact"], i["new_email"]),
    "search_knowledge":        lambda i: _search_knowledge(i["query"]),
}


def execute_tool(name: str, inputs: dict) -> str:
    handler = _TOOL_MAP.get(name)
    if not handler:
        return f"Unknown tool: {name}"
    try:
        return handler(inputs)
    except KeyError as e:
        return f"Error: missing required input {e}. Please retry with the correct parameters."
    except Exception as e:
        return f"Error: {e}. Please retry."
