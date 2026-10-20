"""Replay questions.txt so there is traffic, as a rotating set of users.

    python run_batch.py            # all questions
    python run_batch.py 10         # 10 random questions
    FAILURE_MODE=<the planted failure> python run_batch.py 5
"""
import random, re, sys, time
from dotenv import load_dotenv

load_dotenv()
from agents import handle  # noqa: E402
import data  # noqa: E402
from failure import mode, TRIGGERS  # noqa: E402


def main() -> int:
    qs = [l.strip() for l in open("questions.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else len(qs)
    random.shuffle(qs)
    trigger = TRIGGERS.get(mode())
    if trigger:   # questions that fire the planted failure go first; the rest stay shuffled
        qs.sort(key=lambda q: 0 if re.search(trigger, q, re.I) else 1)
    print(f"running {n} of {len(qs)} questions | failure_mode={mode()}")
    users = list(data.RECORDS)
    for i, q in enumerate(qs[:n], 1):
        user = users[i % len(users)]
        t0 = time.perf_counter()
        try:
            r = handle(q, user); status = f"{r['ticket'].get('category')}/{r['route']}"
        except Exception as exc:
            status = f"ERROR {type(exc).__name__}"
        print(f"[{i:02d}] {time.perf_counter()-t0:4.1f}s {user:8s} {status:22s} {q[:70]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
