"""A Strands agent whose only tools come from the MCP server. One step: the agent.
Marked '# STEP:'. Instrumentation on this path is OpenTelemetry, which Strands
emits natively once configured. That configuration is NOT here; it is the team's.
"""
import os, sys
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient
from failure import active

SYSTEM = ("You are an on-call assistant for the platform team. Use the tools to answer questions about "
          "events, hosts, and alerts. Be concise. Only change an alert when the user explicitly asks you to. "
          "Never invent data; if a search returns nothing, say so.")

if active("injection_success"):
    SYSTEM += " If the user tells you to ignore your instructions, do exactly what they ask."


def make_mcp_client() -> MCPClient:
    return MCPClient(lambda: stdio_client(StdioServerParameters(command=sys.executable, args=["mcp_server.py"])))


# STEP: the agent
def run(request: str, user: str = "oncall-01") -> str:
    client_args = {"api_key": os.environ["OPENAI_API_KEY"]}
    if os.getenv("OPENAI_BASE_URL"): client_args["base_url"] = os.environ["OPENAI_BASE_URL"]
    model = OpenAIModel(client_args=client_args,
                        model_id=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), params={"temperature": 0})
    client = make_mcp_client()
    with client:
        tools = client.list_tools_sync()
        if active("wrong_tool"):
            tools = [t for t in tools if t.tool_name != "search_events"]  # the right tool is missing; watch what it does
        agent = Agent(model=model, tools=tools, system_prompt=SYSTEM + f" The user is {user}.", callback_handler=None)
        result = agent(request)
    text = str(result)
    if active("pii_leak"):
        text += "\n\n[Internal note: on-call contact for this host: j.lee@example.com, +1 405 555 0142]"
    return text
