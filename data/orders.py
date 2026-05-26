ORDERS = {
    # Sarah Chen's orders
    "BK-2001": {
        "status": "delivered",
        "delivered_on": "2026-05-27",
        "items": ["The Great Gatsby", "1984"],
        "total": "$24.98",
        "customer": "Sarah Chen",
    },
    "BK-2002": {
        "status": "delayed",
        "tracking_number": "TRK-334455",
        "original_delivery": "2026-06-01",
        "items": ["Dune Messiah"],
        "total": "$14.99",
        "customer": "Sarah Chen",
    },

    # John Doe's orders
    "BK-3001": {
        "status": "delayed",
        "tracking_number": "1Z9V84W30342958701",
        "original_delivery": "2026-05-29",
        "items": ["Atomic Habits"],
        "total": "$16.99",
        "customer": "John Doe",
        "delay_reason": "Delayed at UPS Memphis, TN facility due to severe weather. New estimated delivery: June 2nd.",
    },
    "BK-3002": {
        "status": "delivered",
        "delivered_on": "2026-05-27",
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
        entry["delay_reason"] = order.get("delay_reason", "Shipment is delayed — flagged as stuck in transit by carrier.")
    return entry


def get_orders_by_contact(contact: str) -> str:
    import json
    from data.auth import CUSTOMERS
    customer = CUSTOMERS.get(contact.strip().lower())
    if not customer:
        return json.dumps({"success": False, "error": f"No account found for '{contact}'."})

    orders = [_format_order(oid, ORDERS[oid]) for oid in customer["orders"] if oid in ORDERS]
    return json.dumps({"customer": customer["name"], "orders": orders})


def initiate_exchange_request(order_id: str, reason: str) -> str:
    import json
    order = ORDERS.get(order_id.upper())
    if not order:
        return json.dumps({"success": False, "error": f"No order found with ID '{order_id}'."})

    exchange_id = f"EXC-{order_id.upper()}-{abs(hash(reason)) % 10000:04d}"
    return json.dumps({
        "success": True,
        "exchange_id": exchange_id,
        "order_id": order_id.upper(),
        "message": "Exchange initiated successfully.",
        "next_steps": [
            "A prepaid return label will be emailed within 24 hours.",
            "A replacement will be shipped as soon as we receive the original.",
        ],
    })


def initiate_return_request(order_id: str, reason: str) -> str:
    import json
    order = ORDERS.get(order_id.upper())
    if not order:
        return json.dumps({"success": False, "error": f"No order found with ID '{order_id}'."})

    if order["status"] not in ("delivered",):
        return json.dumps({
            "success": False,
            "error": f"Order {order_id.upper()} cannot be returned yet — it has not been delivered.",
            "current_status": order["status"],
        })

    return json.dumps({
        "success": True,
        "order_id": order_id.upper(),
        "message": "Return successfully initiated.",
        "next_steps": [
            "A prepaid shipping label will be emailed within 24 hours.",
            "Refund will be processed within 3-5 business days of receiving the item.",
        ],
    })
