"""Command-line chat with the agent.   python app.py "which hosts are degraded?" """
import sys
from dotenv import load_dotenv

load_dotenv()
from agent import run  # noqa: E402
from failure import mode  # noqa: E402


def main() -> int:
    print(f"[agent ready | failure_mode={mode()}]")
    if len(sys.argv) > 1:
        print("\n" + run(" ".join(sys.argv[1:])))
        return 0
    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if not q or q in ("exit", "quit"):
            return 0
        print("\n" + run(q))


if __name__ == "__main__":
    sys.exit(main())
