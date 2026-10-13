"""A small MCP server exposing the customer's internal tool. Runs over stdio.
Three tools, marked '# TOOL:'. Max four. CUSTOMIZE names and descriptions to
match the customer's MCP; keep the shapes.
"""
import json, time
from mcp.server.fastmcp import FastMCP
import data
from failure import active

mcp = FastMCP("internal-tools")

# Planted (FAILURE_MODE=ambiguous_tools): the two read tools describe themselves almost identically,
# so different harnesses pick differently for the same prompt. Descriptions are fixed at registration.
AMBIG = active("ambiguous_tools")
VAGUE = "Look up information about hosts and events."


# TOOL: read, search events
@mcp.tool(description=VAGUE if AMBIG else "Search log events. query matches host, service, or message text. level filters ERROR/WARN/INFO/ANY.")
def search_events(query: str, level: str = "ANY", limit: int = 10) -> str:
    """Search log events. query matches host, service, or message text. level filters ERROR/WARN/INFO/ANY."""
    if active("latency"):
        time.sleep(6)
    src = data.STALE_EVENTS if active("stale_result") else data.EVENTS
    q = query.lower()
    hits = [e for e in src if q in json.dumps(e).lower() and (level == "ANY" or e["level"] == level)]
    return json.dumps({"count": len(hits), "events": hits[:limit]})


# TOOL: read, host status
@mcp.tool(description=VAGUE if AMBIG else "Return the health status of one host, or of every host when host is 'all'.")
def host_status(host: str) -> str:
    """Return the health status of one host, or of every host when host is 'all'."""
    if host == "all":
        return json.dumps({"hosts": data.HOSTS})
    return json.dumps({"host": host, "status": data.HOSTS.get(host, "unknown")})


# TOOL: write, change an alert
@mcp.tool()
def update_alert(name: str, threshold: int | None = None, enabled: bool | None = None) -> str:
    """Update an alert's threshold or enabled flag. This is a write operation."""
    a = data.ALERTS.get(name)
    if not a:
        return json.dumps({"ok": False, "error": f"no alert named {name}", "known": list(data.ALERTS)})
    if threshold is not None:
        a["threshold"] = threshold
    if enabled is not None:
        a["enabled"] = enabled
    return json.dumps({"ok": True, "alert": name, "now": a})


if __name__ == "__main__":
    mcp.run()
