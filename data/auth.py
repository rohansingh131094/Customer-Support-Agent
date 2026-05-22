# Mock customer directory — keyed by email or phone
CUSTOMERS = {
    "sarah@gmail.com": {"name": "Sarah Chen", "orders": ["BK-2001", "BK-2002"]},
    "555-0201":          {"name": "Sarah Chen", "orders": ["BK-2001", "BK-2002"]},
    "john@gmail.com": {"name": "John Doe", "orders": ["BK-3001", "BK-3002"]},
    "555-0301":         {"name": "John Doe", "orders": ["BK-3001", "BK-3002"]},
}

# In-memory OTP store: {contact: "pending"}
_pending_otps: dict = {}


def send_otp(contact: str) -> str:
    contact = contact.strip().lower()
    if contact not in CUSTOMERS:
        return (
            f"No account found for '{contact}'. "
            "Please check the email or phone number and try again."
        )

    _pending_otps[contact] = "demo"
    return (
        f"Code sent to {contact}. "
        f"(Demo: enter any 6-digit code to verify.)"
    )


def verify_otp(contact: str, code: str) -> str:
    contact = contact.strip().lower()
    code = code.strip()

    if not code.isdigit() or len(code) != 6:
        return "Please enter a valid 6-digit code."

    if contact not in _pending_otps:
        return "No pending verification for that contact. Please request a new code."

    del _pending_otps[contact]

    customer = CUSTOMERS[contact]
    orders_str = ", ".join(customer["orders"])
    return (
        f"Verified. Customer: {customer['name']}. "
        f"Orders on this account: {orders_str}"
    )
