# checkout-service

Handles cart checkout for the storefront. On `POST /checkout` it validates the cart, reserves
inventory, and charges the customer through the payment gateway.

## Running locally

```
pip install -r requirements.txt
flask --app app.main run --port 8080
```

## Configuration

Settings live in `config/settings.yaml` and can be overridden with environment variables of the
same name (upper-cased).

| Setting | Purpose |
| --- | --- |
| `payment_gateway_url` | Base URL of the payment gateway |
| `payment_timeout_ms` | Per-request timeout for payment gateway calls |
| `payment_max_retries` | Retries on payment gateway timeouts / 5xx |
| `inventory_url` | Base URL of the inventory service |

## On-call runbook

- **Checkout 5xx spike:** check `checkout failed` log lines for the failing dependency, then the
  payment gateway and inventory status pages.
- **Inventory 409s:** usually a stuck reservation sweeper on the inventory side; page the
  inventory team.
