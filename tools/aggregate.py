import argparse, glob, json, os
import numpy as np
import pandas as pd

def summarize_one(set_name: str, tag: str):
    pattern = f"metrics/prompt_eval_{set_name}_{tag}_*.csv"
    files = sorted(glob.glob(pattern))
    if not files:
        raise SystemExit(f"Not found: {pattern}")

    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

    n = len(df)
    ok = df["ok"].astype(bool) if "ok" in df.columns else pd.Series([True]*n)
    lat = df["latency_ms"] if "latency_ms" in df.columns else None

    def pct(series, p):
        if series is None or series.dropna().empty:
            return None
        return float(np.percentile(series.dropna(), p))

    out = {
        "set": set_name,
        "tag": tag,
        "n": int(n),
        "pass_ratio": float(ok.mean()) if n else 0.0,   # 성공 비율(평균 ok)
        "p50_ms": round(pct(lat[ok], 50), 2) if lat is not None else None,
        "p95_ms": round(pct(lat[ok], 95), 2) if lat is not None else None,
    }

    # 있으면 자동 집계
    if "json_ok" in df.columns:
        out["json_ok"] = round(float(df["json_ok"].mean()*100), 1)  # %
    if "key_coverage" in df.columns:
        out["coverage"] = round(float(df["key_coverage"].mean()*100), 1)  # %
    if "accuracy" in df.columns:
        out["accuracy"] = round(float(df["accuracy"].mean()*100), 1)  # %

    os.makedirs("metrics", exist_ok=True)
    outpath = f"metrics/summary_{set_name}_{tag}.json"
    with open(outpath, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[OK] summary saved: {outpath}")
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", required=True, help="comma-separated (e.g., baseline,structured)")
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    results = []
    for s in [x.strip() for x in args.sets.split(",") if x.strip()]:
        results.append(summarize_one(s, args.tag))

    # 간단 비교 표 출력
    def get(d, k): return d.get(k, None)
    keys = ["n","pass_ratio","p50_ms","p95_ms","json_ok","coverage","accuracy"]
    df = pd.DataFrame([{**{k:get(d,k) for k in keys}, "set": d["set"]} for d in results])
    cols = ["set"] + keys
    print("\n=== SUMMARY ===")
    print(df[cols].to_string(index=False))

if __name__ == "__main__":
    main()