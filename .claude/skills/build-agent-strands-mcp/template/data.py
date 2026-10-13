"""Mock data behind the MCP server. CUSTOMIZE for the customer's internal tools.
This one mimics an internal observability platform: saved searches, alerts, hosts.
"""

# CUSTOMIZE: things the tools can search over. Fictional.
EVENTS = [
    {"host": "web-01", "service": "checkout", "level": "ERROR", "msg": "payment gateway timeout after 30s", "ts": "2026-09-30T14:02:11Z"},
    {"host": "web-02", "service": "checkout", "level": "ERROR", "msg": "payment gateway timeout after 30s", "ts": "2026-09-30T14:02:14Z"},
    {"host": "api-07", "service": "inventory", "level": "WARN", "msg": "cache miss rate 41%", "ts": "2026-09-30T14:03:40Z"},
    {"host": "db-03", "service": "orders", "level": "ERROR", "msg": "deadlock detected on orders_pk", "ts": "2026-09-30T14:05:02Z"},
    {"host": "web-01", "service": "checkout", "level": "INFO", "msg": "deploy v2.14.0 complete", "ts": "2026-09-30T13:58:00Z"},
    {"host": "auth-01", "service": "sso", "level": "ERROR", "msg": "token validation failed: clock skew", "ts": "2026-09-30T14:06:30Z"},
]

# CUSTOMIZE: alerts the write tool can modify. Fictional.
ALERTS = {
    "checkout-5xx": {"threshold": 50, "window": "5m", "owner": "payments", "enabled": True},
    "orders-deadlock": {"threshold": 1, "window": "1m", "owner": "data", "enabled": True},
    "sso-failures": {"threshold": 20, "window": "10m", "owner": "identity", "enabled": False},
}

HOSTS = {"web-01": "ok", "web-02": "degraded", "api-07": "ok", "db-03": "degraded", "auth-01": "ok"}

# Planted stale result (FAILURE_MODE=stale_result): the search tool returns yesterday's data.
STALE_EVENTS = [{"host": "web-01", "service": "checkout", "level": "INFO", "msg": "all clear", "ts": "2026-09-29T14:02:11Z"}]
