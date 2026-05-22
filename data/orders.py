ORDERS = {
    # Sarah Chen's orders
    "BK-2001": {
        "status": "delivered",
        "delivered_on": "2026-05-18",
        "items": ["The Great Gatsby", "1984"],
        "total": "$24.98",
        "customer": "Sarah Chen",
    },
    "BK-2002": {
        "status": "delayed",
        "tracking_number": "TRK-334455",
        "original_delivery": "2026-05-20",
        "items": ["Dune Messiah"],
        "total": "$14.99",
        "customer": "Sarah Chen",
    },

    # John Doe's orders
    "BK-3001": {
        "status": "shipped",
        "tracking_number": "TRK-667788",
        "estimated_delivery": "2026-05-24",
        "items": ["Atomic Habits"],
        "total": "$16.99",
        "customer": "John Doe",
    },
    "BK-3002": {
        "status": "delivered",
        "delivered_on": "2026-05-19",
        "items": ["Deep Work", "Digital Minimalism"],
        "total": "$31.98",
        "customer": "John Doe",
    },
}


def _format_order(order_id: str, order: dict) -> dict:
    entry = {
        "order_id": order_id.upper(),
        "status": order["status"],
        "items": order["items"],
        "total": order["total"],
    }
    if order["status"] == "shipped":
        entry["tracking_number"] = order["tracking_number"]
        entry["estimated_delivery"] = order["estimated_delivery"]
    elif order["status"] == "delivered":
        entry["delivered_on"] = order["delivered_on"]
    elif order["status"] == "processing":
        entry["estimated_ship"] = order.get("estimated_ship")
    elif order["status"] == "delayed":
        entry["tracking_number"] = order["tracking_number"]
        entry["original_delivery"] = order["original_delivery"]
        entry["note"] = "Shipment is delayed — flagged as stuck in transit by carrier."
    return entry


def get_orders_by_contact(contact: str) -> str:
    import json
    from data.auth import CUSTOMERS
    customer = CUSTOMERS.get(contact.strip().lower())
    if not customer:
        return f"No account found for '{contact}'."
    orders = [_format_order(oid, ORDERS[oid]) for oid in customer["orders"] if oid in ORDERS]
    return json.dumps({"customer": customer["name"], "orders": orders})


def initiate_exchange_request(order_id: str, reason: str) -> str:
    order = ORDERS.get(order_id.upper())
    if not order:
        return f"No order found with ID '{order_id}'."

    exchange_id = f"EXC-{order_id.upper()}-{abs(hash(reason)) % 10000:04d}"
    return (
        f"Exchange initiated successfully for order {order_id.upper()}. "
        f"A prepaid return label will be emailed within 24 hours. "
        f"A replacement will be shipped as soon as we receive the original. "
        f"Exchange reference: {exchange_id}."
    )


def initiate_return_request(order_id: str, reason: str) -> str:
    order = ORDERS.get(order_id.upper())
    if not order:
        return f"No order found with ID '{order_id}'."

    if order["status"] not in ("delivered",):
        return (
            f"Order {order_id.upper()} cannot be returned yet — it has not been delivered "
            f"(current status: {order['status'].replace('_', ' ')}). "
            f"Please wait until the order is delivered before requesting a return."
        )

    return (
        f"Return successfully initiated for order {order_id.upper()}. "
        f"A prepaid shipping label will be emailed within 24 hours. "
        f"The refund will be processed within 3-5 business days of receiving the item."
    )
