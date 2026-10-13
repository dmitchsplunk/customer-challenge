"""Command-line chat with the agent.

    python app.py
    python app.py "When is my next pay date?"

No observability code here on purpose. See README.md, "What you still have to do".
"""
import os, sys
from dotenv import load_dotenv

load_dotenv()
from agents import handle  # noqa: E402
from failure import mode  # noqa: E402

USER_ID = os.getenv("DEMO_USER_ID", "E-10001")


def main() -> int:
    print(f"[agent ready | failure_mode={mode()} | user={USER_ID}]")
    if len(sys.argv) > 1:
        r = handle(" ".join(sys.argv[1:]), USER_ID)
        print(f"\n[{r['ticket'].get('category')} / {r['route']}]\n{r['reply']}")
        return 0
    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if not q or q in ("exit", "quit"):
            return 0
        r = handle(q, USER_ID)
        print(f"\n[{r['ticket'].get('category')} / {r['route']}]\n{r['reply']}")


if __name__ == "__main__":
    sys.exit(main())
