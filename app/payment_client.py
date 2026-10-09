import logging

import requests

log = logging.getLogger(__name__)


class PaymentError(Exception):
    pass


class PaymentClient:
    def __init__(self, base_url: str, timeout_ms: int, max_retries: int):
        self.base_url = base_url
        self.timeout_s = timeout_ms / 1000
        self.max_retries = max_retries
        self.session = requests.Session()

    def charge(self, customer_id: str, amount_cents: int, idempotency_key: str) -> str:
        attempts = self.max_retries + 1
        for attempt in range(1, attempts + 1):
            try:
                resp = self.session.post(
                    f"{self.base_url}/v1/charges",
                    json={"customer_id": customer_id, "amount_cents": amount_cents},
                    headers={"Idempotency-Key": idempotency_key},
                    timeout=self.timeout_s,
                )
                if resp.status_code >= 500:
                    raise PaymentError(f"gateway returned {resp.status_code}")
                resp.raise_for_status()
                return resp.json()["charge_id"]
            except (requests.Timeout, PaymentError) as e:
                log.warning("payment attempt %d/%d failed: %s", attempt, attempts, e)
                if attempt == attempts:
                    raise PaymentError("payment gateway unavailable") from e
