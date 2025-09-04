
# 🧪 LLM Prompt Engineering Bench: 구조화 프롬프트 실험

LLM 프롬프트를 **세트(baseline vs structured JSON)** 로 나눠 벤치마크하고,  
지연시간/일관성/정확성을 수치로 비교해 보는 실험형 프로젝트입니다.

---

## 🧠 개요 (Overview)

- 동일 입력에 대해 **프롬프트 구조**를 바꿨을 때 모델 응답이 어떻게 달라지는지 측정
- **JSON 스키마 강제**로 출력 일관성 및 자동 평가 가능성 확인
- 실험 결과를 CSV/JSON으로 남기고, **before/after 델타**까지 자동 계산

---

## 🎯 실험 목적 (Objective)

- baseline(자유서술) ↔ structured(JSON 강제) 프롬프트의 **지연시간·일치율** 비교
- 요약/분류/추출 등 **일반화 태스크**에 재사용 가능한 벤치 파이프라인 구축
- 지원서/포트폴리오에 넣을 수 있는 **재현 가능한 수치** 생성

---

## 🗂 폴더 구조
```text
LLM-Prompt-Test/
├── data/
│ └── tasks.csv # 테스트 태스크(요약/분류/추출)
├── metrics/ # 결과물(요약 JSON, 평가 CSV)
├── prompts/
│ ├── registry.py # 세트 등록(baseline, structured)
│ └── sets/
│ ├── baseline.py # 자유서술형(비 JSON)
│ └── structured_json.py # 구조화 응답(JSON 스키마 강제)
├── tools/
│ ├── prompt_bench.py # 벤치 러너
│ ├── aggregate.py # 세트별 요약 집계(JSON)
│ └── compare.py # before/after 델타 비교
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 📦 설치 & 준비

```bash
# 의존성
pip install -r requirements.txt

# (필수) OpenAI API Key
# - Git Bash / macOS / Linux
export OPENAI_API_KEY="sk-..."
# - PowerShell
# $env:OPENAI_API_KEY="sk-..."
```

---

## 🧪 실행 방법
1) 드라이런(무료/품질 점검)
```bash
python -m tools.prompt_bench --sets baseline,structured --dry-run 1 --tag smoke --tasks data/tasks.csv
```
- 네트워크 호출 없이 프롬프트 메시지 구성만 검증

2) 실측(유료 호출)
```bash
python -m tools.prompt_bench --sets baseline,structured --tag v1 --tasks data/tasks.csv
```
- 세트별 실행 로그와 metrics/prompt_eval_*.csv 생성

3) 집계(세트별 요약 JSON)
```bash
python -m tools.aggregate --sets baseline,structured --tag v1
# -> metrics/summary_baseline_v1.json
# -> metrics/summary_structured_v1.json
```

4) 비교(델타 리포트)
```bash
python -m tools.compare --tag v1
```
- p50_ms, p95_ms, json_ok, coverage, accuracy 등 after vs before 차이 출력
- coverage/accuracy는 라벨링이 있는 행에만 계산됩니다.

---

## 🧾 데이터 포맷 (data/tasks.csv)
```csv
id,task,input,expected_label,key_terms,max_len,expected_name,expected_email,expected_phone
1,summarization,"신규 업데이트 공지...",,핵심,업데이트|성능,120,,
2,classification,"서비스가 느리고 오류가 많아요",positive,,,
```

---

## 📊 예시 결과
| set        | n | pass\_ratio | p50\_ms | p95\_ms | json\_ok | coverage | accuracy |
| ---------- | - | ----------- | ------- | ------- | -------- | -------- | -------- |
| baseline   | 6 | 1.0         | 1167.25 | 2766.89 | —        | —        | —        |
| structured | 6 | 1.0         | 166.67  | 870.00  | 100.0    | —        | —        |

Deltas (after vs before, structured vs baseline)
- p50_ms: -85.7%
- p95_ms: -68.6%
- json_ok: +100.0%
> (coverage/accuracy는 라벨 추가 후 활성)

---

🧩 확장 아이디어
- 분류 레이블 다중 클래스화(label: A|B|C) 및 정확도 측정
- 추출 태스크에 정밀/재현율 계산 로직 추가
- 비용/토큰 사용량 비교(추가 지표)
- 다양한 모델/파라미터(temperature 등) 비교 세트 추가

🛠 트러블슈팅
- ModuleNotFoundError: prompts
  - 패키지로 인식되도록 prompts/__init__.py, prompts/sets/__init__.py 존재 확인
  - 모듈 실행은 python -m tools.prompt_bench ... 형태로 수행
- data/tasks.csv not found
  - 상대경로 기준: 프로젝트 루트에서 실행해야 함
  - 경로/파일명 오타 확인
 
👤 작성자

- 오성빈 / OH-SEONGBIN
- 문의/피드백: GitHub Issues
