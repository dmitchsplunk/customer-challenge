from typing import Literal, Optional, TypedDict


class Ticket(TypedDict):
    title: str
    category: str
    urgency: str


class State(TypedDict, total=False):
    request: str
    user_id: str
    ticket: Ticket
    route: Literal["knowledge", "action", "escalate"]
    articles: list[dict]
    tool_result: str
    reply: str
