import argparse, csv, json, os, time, datetime, sys, random
from typing import Dict, Any, List
import pandas as pd

# ---- OpenAI v1 client (pip install openai>=1.10.0)
try:
    import openai
    _CLIENT = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    _CLIENT = None  # 드라이런 또는 키 미설정 시 사용 안함

# 내부 모듈
from prompts.registry import get_prompt_set  # 이미 만들어둔 레지스트리 사용

def now_ts():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

def call_openai(messages: List[Dict[str, str]], model: str, json_mode: bool, timeout: int = 60) -> Dict[str, Any]:
    """
    OpenAI 실제 호출. json_mode=True면 response_format=json_object로 요청.
    간단 리트라이(backoff) 포함.
    """
    if _CLIENT is None:
        raise RuntimeError("OpenAI client not available (missing package or OPENAI_API_KEY)")

    for attempt in range(3):
        try:
            kwargs = dict(model=model, messages=messages, temperature=0.2, timeout=timeout)
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            t0 = time.perf_counter()
            resp = _CLIENT.chat.completions.create(**kwargs)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            text = resp.choices[0].message.content or ""
            return {"ok": True, "text": text, "latency_ms": elapsed_ms}
        except Exception as e:
            if attempt == 2:
                return {"ok": False, "text": str(e)[:500], "latency_ms": None}
            time.sleep(1.5 * (attempt + 1))  # 간단 backoff

def dry_run_reply(row: Dict[str, Any], json_mode: bool) -> str:
    """모델 호출 없이 빠른 더미 응답(무료)."""
    t = (row.get("task_input") or row.get("input") or row.get("text") or "").strip()
    t = " ".join(t.split())
    if json_mode:
        # 구조화 세트: JSON 흉내 (검증용)
        return json.dumps({"summary": (t[:80] + "…") if len(t) > 80 else t, "label": "positive"}, ensure_ascii=False)
    else:
        # 베이스라인: 자유 텍스트
        return (t[:120] + "…") if len(t) > 120 else t

def run_one_set(set_name: str, df: pd.DataFrame, tag: str, dry_run: bool, model: str, limit: int):
    ps = get_prompt_set(set_name)  # PromptSet: build(row)->(messages, json_mode)
    out_rows = []
    n = len(df) if not limit else min(limit, len(df))
    for i in range(n):
        row = df.iloc[i].to_dict()
        messages, json_mode = ps.build(row)

        if dry_run:
            t0 = time.perf_counter()
            text = dry_run_reply(row, json_mode)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            ok = True
        else:
            r = call_openai(messages, model=model, json_mode=json_mode)
            ok, text, latency_ms = r["ok"], r["text"], r["latency_ms"]

        json_ok = False
        if ok and json_mode:
            try:
                json.loads(text)
                json_ok = True
            except Exception:
                json_ok = False

        out_rows.append({
            "set": set_name,
            "id": row.get("id"),
            "task": row.get("task"),
            "latency_ms": round(latency_ms or 0.0, 2),
            "ok": bool(ok),
            "json_ok": json_ok,
            "output": text
        })
        print(f"[{i+1}/{n}] {set_name} {latency_ms if latency_ms else 0:.2f}ms ok={ok}")

    os.makedirs("metrics", exist_ok=True)
    ts = now_ts()
    out_path = f"metrics/prompt_eval_{set_name}_{tag}_{ts}.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)
    print(f"[OK] saved: {out_path} (total≈{round(sum([r['latency_ms'] or 0 for r in out_rows]),1)}ms, n={len(out_rows)})")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", required=True, help="예: baseline,structured")
    ap.add_argument("--tag", default="run", help="결과 파일명 구분용 태그")
    ap.add_argument("--tasks", default="data/tasks.csv", help="태스크 CSV 경로")
    ap.add_argument("--dry-run", type=int, default=0, help="1=드라이런(무료), 0=실제 호출")
    ap.add_argument("--model", default=os.environ.get("MODEL", "gpt-4o-mini"))
    ap.add_argument("--limit", type=int, default=0, help="0=전체, >0=상위 N건만 실행")
    args = ap.parse_args()

    # 데이터 읽기 (id, task, input/ task_input ... 열 지원)
    # 샘플 CSV는 data/tasks.csv 참고
    if not os.path.exists(args.tasks):
        sys.exit(f"Not found: {args.tasks}")
    df = pd.read_csv(args.tasks)

    sets = [s.strip() for s in args.sets.split(",") if s.strip()]
    for s in sets:
        run_one_set(s, df, args.tag, bool(args.dry_run), args.model, args.limit)

if __name__ == "__main__":
    main()