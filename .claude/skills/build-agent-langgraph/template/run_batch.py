"""Replay questions.txt through the agent so there is traffic to look at.

    python run_batch.py            # all questions
    python run_batch.py 10         # first 10
    FAILURE_MODE=<the planted failure> python run_batch.py 5

Each question runs as a different user from data.RECORDS so that anything you
group per user later has several users in it.
"""
import random, sys, time
from dotenv import load_dotenv

load_dotenv()
from app import ask  # noqa: E402
import data  # noqa: E402
from agent.graph import build_graph  # noqa: E402
from failure import mode  # noqa: E402


def main() -> int:
    qs = [l.strip() for l in open("questions.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else len(qs)
    random.shuffle(qs)
    graph = build_graph()
    print(f"running {n} of {len(qs)} questions | failure_mode={mode()}")
    users = list(data.RECORDS)
    for i, q in enumerate(qs[:n], 1):
        user = users[i % len(users)]
        t0 = time.perf_counter()
        try:
            r = ask(graph, q, user); status = f"{r['ticket']['category']}/{r['route']}"
        except Exception as exc:
            status = f"ERROR {type(exc).__name__}"
        print(f"[{i:02d}] {time.perf_counter()-t0:4.1f}s {user:8s} {status:22s} {q[:70]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
