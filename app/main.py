import logging
import uuid

import requests
from flask import Flask, jsonify, request

from app.config import load_settings
from app.payment_client import PaymentClient, PaymentError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

settings = load_settings()
app = Flask(__name__)
payments = PaymentClient(
    settings["payment_gateway_url"],
    settings["payment_timeout_ms"],
    settings["payment_max_retries"],
)


@app.get("/healthz")
def healthz():
    return "ok"


@app.post("/checkout")
def checkout():
    body = request.get_json()
    cart = body["cart"]
    if not cart["items"]:
        return jsonify(error="empty cart"), 400

    reserve = requests.post(f"{settings['inventory_url']}/v1/reservations", json=cart, timeout=2)
    if reserve.status_code != 200:
        return jsonify(error="inventory unavailable"), 409

    total = sum(item["price_cents"] * item["quantity"] for item in cart["items"])
    try:
        charge_id = payments.charge(body["customer_id"], total, idempotency_key=str(uuid.uuid4()))
    except PaymentError:
        log.exception("checkout failed for customer %s", body["customer_id"])
        return jsonify(error="payment failed"), 502

    return jsonify(order_id=str(uuid.uuid4()), charge_id=charge_id)
