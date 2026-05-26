import json
import chromadb

_collection = None

# Knowledge documents — each chunk covers one specific topic/scenario
DOCUMENTS = [
    # ── Shipping ────────────────────────────────────────────────────────────
    {
        "id": "shipping-standard",
        "text": (
            "Standard shipping takes 5-7 business days and is free on orders over $35. "
            "Orders placed before 2pm ET ship the same day."
        ),
        "topic": "shipping",
    },
    {
        "id": "shipping-expedited",
        "text": (
            "Expedited shipping (2-3 business days) is available for $9.99. "
            "Express shipping (next business day) is available for $19.99."
        ),
        "topic": "shipping",
    },
    {
        "id": "shipping-tracking",
        "text": (
            "Once your order ships, you will receive a tracking number by email. "
            "You can use this to track your package on the carrier's website. "
            "If your tracking hasn't updated in 3 business days, contact support."
        ),
        "topic": "shipping",
    },
    {
        "id": "shipping-lost",
        "text": (
            "If your package has not arrived within 10 business days of the estimated delivery date, "
            "it may be lost in transit. Contact Bookly support with your order ID to open a claim. "
            "We will either reship the order or issue a full refund."
        ),
        "topic": "shipping",
    },

    # ── Returns & Refunds ────────────────────────────────────────────────────
    {
        "id": "returns-window",
        "text": (
            "Items can be returned within 30 days of delivery for a full refund. "
            "Orders outside the 30-day window are not eligible for a return."
        ),
        "topic": "returns",
    },
    {
        "id": "returns-condition",
        "text": (
            "Books must be in original, unread condition and in their original packaging to be eligible for a return. "
            "Items that show signs of use, damage caused by the customer, or missing packaging may be refused."
        ),
        "topic": "returns",
    },
    {
        "id": "returns-process",
        "text": (
            "To initiate a return, provide your order ID and the reason for the return. "
            "A prepaid return shipping label will be emailed within 24 hours. "
            "Refunds are processed within 5-7 business days of receiving the returned item "
            "and are issued to the original payment method."
        ),
        "topic": "returns",
    },
    {
        "id": "returns-damaged",
        "text": (
            "If your item arrived damaged or defective, you are eligible for a full refund or a free exchange "
            "regardless of the item's condition."
        ),
        "topic": "returns",
    },
    {
        "id": "returns-digital",
        "text": (
            "Digital items such as e-books and audiobooks are not eligible for return or refund once accessed. "
            "If you purchased a digital item by mistake and have not accessed it, contact support within 24 hours."
        ),
        "topic": "returns",
    },
    {
        "id": "returns-gift",
        "text": (
            "Gift items can be returned for store credit only. "
            "Refunds are not issued to the original purchaser for gift returns."
        ),
        "topic": "returns",
    },

    # ── Payment ──────────────────────────────────────────────────────────────
    {
        "id": "payment-methods",
        "text": (
            "Bookly accepts Visa, Mastercard, American Express, Discover, and PayPal. "
            "Gift cards can be applied at checkout."
        ),
        "topic": "payment",
    },
    {
        "id": "payment-security",
        "text": (
            "All transactions are secured with 256-bit SSL encryption. "
            "Bookly does not store full credit card numbers. "
            "Your payment information is processed by a PCI-compliant payment provider."
        ),
        "topic": "payment",
    },
    {
        "id": "payment-failed",
        "text": (
            "If your payment fails at checkout, check that your billing address matches your card on file. "
            "Try a different payment method or contact your bank. "
            "Bookly does not charge your card until the order is confirmed."
        ),
        "topic": "payment",
    },
    {
        "id": "payment-gift-cards",
        "text": (
            "Bookly gift cards can be purchased in denominations of $10, $25, $50, and $100. "
            "Gift cards do not expire and can be combined with other payment methods at checkout. "
            "Lost or stolen gift cards cannot be replaced."
        ),
        "topic": "payment",
    },

    # ── Account & Password ───────────────────────────────────────────────────
    {
        "id": "account-password-reset",
        "text": (
            "To reset your password, visit bookly.com/reset and enter your email address. "
            "You will receive a reset link within 5 minutes. "
            "If you do not see the email, check your spam folder."
        ),
        "topic": "account",
    },
    {
        "id": "account-password-help",
        "text": (
            "If you are locked out of your account or did not receive a password reset email, "
            "contact support at help@bookly.com. "
            "For security, Bookly support cannot reset your password on your behalf — "
            "the reset must be done through the self-service link."
        ),
        "topic": "account",
    },
    {
        "id": "account-general",
        "text": (
            "You can update your email address, shipping address, and payment methods from your account settings. "
            "To close your account, contact support at help@bookly.com."
        ),
        "topic": "account",
    },
]


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = chromadb.Client()
        _collection = client.get_or_create_collection("bookly_knowledge")
        _collection.add(
            documents=[d["text"] for d in DOCUMENTS],
            ids=[d["id"] for d in DOCUMENTS],
            metadatas=[{"topic": d["topic"]} for d in DOCUMENTS],
        )
    return _collection


def search_knowledge(query: str, n_results: int = 3) -> str:
    collection = _get_collection()
    results = collection.query(query_texts=[query], n_results=min(n_results, len(DOCUMENTS)))
    docs = results.get("documents", [[]])[0]
    if not docs:
        return json.dumps({"success": False, "error": "No relevant information found in the Bookly knowledge base."})
    return json.dumps({"results": docs})
