from langgraph.graph import END, StateGraph
from .nodes import intake, route, resolve, write
from .state import State


def build_graph():
    g = StateGraph(State)
    g.add_node("intake", intake)
    g.add_node("route", route)
    g.add_node("resolve", resolve)
    g.add_node("write", write)
    g.set_entry_point("intake")
    g.add_edge("intake", "route")
    g.add_edge("route", "resolve")
    g.add_edge("resolve", "write")
    g.add_edge("write", END)
    return g.compile()
