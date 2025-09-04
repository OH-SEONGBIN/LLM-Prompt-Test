import json, os, argparse

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pct_impr(a, b, lower_is_better=False):
    if a is None or b is None:
        return None
    # lower_is_better: latency처럼 낮을수록 좋은 지표는 (a-b)/a
    num = (a - b) if lower_is_better else (b - a)
    return round((num / a) * 100.0, 1) if a else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--before", default="baseline")
    ap.add_argument("--after",  default="structured")
    args = ap.parse_args()

    a = load(f"metrics/summary_{args.before}_{args.tag}.json")
    b = load(f"metrics/summary_{args.after}_{args.tag}.json")

    print("=== DELTAS (after vs before) ===")
    print(f"pass_ratio: {pct_impr(a.get('pass_ratio'), b.get('pass_ratio'))}% ↑")
    print(f"p50_ms    : {pct_impr(a.get('p50_ms'),    b.get('p50_ms'),    lower_is_better=True)}% ↓")
    print(f"p95_ms    : {pct_impr(a.get('p95_ms'),    b.get('p95_ms'),    lower_is_better=True)}% ↓")
    print(f"json_ok   : {pct_impr(a.get('json_ok'),   b.get('json_ok'))}% ↑")
    print(f"coverage  : {pct_impr(a.get('coverage'), b.get('coverage'))}% ↑")
    print(f"accuracy  : {pct_impr(a.get('accuracy'), b.get('accuracy'))}% ↑")

if __name__ == "__main__":
    main()