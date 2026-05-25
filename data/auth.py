# Mock customer directory — keyed by email or phone
_SARAH = {
    "name": "Sarah Chen",
    "preferred_name": "Sarah",
    "member_since": "2022-08-15",
    "address": "742 Evergreen Terrace, San Francisco, CA 94110",
    "card": "Visa ending in 3847",
    "orders": ["BK-2001", "BK-2002"],
}

_JOHN = {
    "name": "John Doe",
    "preferred_name": "John",
    "member_since": "2021-04-03",
    "address": "15 Oak Avenue, Brooklyn, NY 11201",
    "card": "Mastercard ending in 5291",
    "orders": ["BK-3001", "BK-3002"],
}

CUSTOMERS = {
    "sarah@gmail.com": _SARAH,
    "415-696-3967":    _SARAH,
    "john@gmail.com":  _JOHN,
    "332-275-3252":    _JOHN,
}

# In-memory OTP store: {contact: "pending"}
_pending_otps: dict = {}


def send_otp(contact: str) -> str:
    import json
    contact = contact.strip().lower()
    if contact not in CUSTOMERS:
        return json.dumps({"success": False, "error": f"No account found for '{contact}'. Please check the email or phone number and try again."})

    _pending_otps[contact] = "demo"
    return json.dumps({"success": True, "message": f"Code sent to {contact}.", "note": "Demo: enter any 6-digit code to verify."})


def verify_otp(contact: str, code: str) -> str:
    import json
    contact = contact.strip().lower()
    code = code.strip()

    if not code.isdigit() or len(code) != 6:
        return json.dumps({"success": False, "error": "Please enter a valid 6-digit code."})

    if contact not in _pending_otps:
        return json.dumps({"success": False, "error": "No pending verification for that contact. Please request a new code."})

    del _pending_otps[contact]

    customer = CUSTOMERS[contact]
    return json.dumps({
        "success": True,
        "customer": {
            "name": customer["name"],
            "preferred_name": customer["preferred_name"],
            "member_since": customer["member_since"],
            "address": customer["address"],
            "card": customer["card"],
        },
        "orders": customer["orders"],
    })
