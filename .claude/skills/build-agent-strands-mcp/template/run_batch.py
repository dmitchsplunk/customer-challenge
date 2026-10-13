"""Replay questions.txt so there is traffic.   python run_batch.py [N]"""
import random, sys, time
from dotenv import load_dotenv

load_dotenv()
from agent import run  # noqa: E402
from failure import mode  # noqa: E402


def main() -> int:
    qs = [l.strip() for l in open("questions.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else len(qs)
    random.shuffle(qs)
    print(f"running {n} of {len(qs)} questions | failure_mode={mode()}")
    for i, q in enumerate(qs[:n], 1):
        t0 = time.perf_counter()
        try:
            out = run(q); status = "ok"
        except Exception as exc:
            status = f"ERROR {type(exc).__name__}"
        print(f"[{i:02d}] {time.perf_counter()-t0:4.1f}s {status:10s} {q[:70]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
