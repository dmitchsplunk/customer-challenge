"""Command-line chat with the agent.

    python app.py                      # interactive
    python app.py "<a question from questions.txt>"

The graph is built once per process. Observability wiring is NOT here; that is
your job. See README.md, "What you still have to do".
"""
import os, sys, uuid
from dotenv import load_dotenv

load_dotenv()
from agent.graph import build_graph  # noqa: E402
from failure import mode  # noqa: E402

USER_ID = os.getenv("DEMO_USER_ID", "E-10001")


def ask(graph, request: str, user_id: str = USER_ID) -> dict:
    # INSTRUMENT HERE: attach the callback and your metadata to this call.
    return graph.invoke({"request": request, "user_id": user_id})


def main() -> int:
    graph = build_graph()
    print(f"[agent ready | failure_mode={mode()} | user={USER_ID}]")
    if len(sys.argv) > 1:
        result = ask(graph, " ".join(sys.argv[1:]))
        print(f"\n[{result['ticket']['category']} / {result['route']}]\n{result['reply']}")
        return 0
    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if not q or q in ("exit", "quit"):
            return 0
        result = ask(graph, q)
        print(f"\n[{result['ticket']['category']} / {result['route']}]\n{result['reply']}")


if __name__ == "__main__":
    sys.exit(main())
