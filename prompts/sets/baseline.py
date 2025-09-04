class BaselineSet:
    name = "baseline"

    def system(self, row) -> str | None:
        return "너는 간단/짧게 답하는 어시스턴트야."

    def expects_json(self, row) -> bool:
        return False

    def temperature(self, row) -> float:
        return 0.7

    def user(self, row) -> str:
        task = row["task"]
        text = str(row["input"])
        if task == "summarization":
            return f"다음 텍스트를 간결히 요약해줘:\n{text}"
        if task == "classification":
            return f"문장을 긍정/부정 중 하나로 분류하고 그 단어만 출력해:\n{text}"
        if task == "extraction":
            return f"아래에서 이름, 이메일, 전화번호를 찾아줘:\n{text}"
        raise ValueError(f"Unknown task: {task}")

    # ✅ 반드시 인스턴스 메서드로!
    def build(self, row):
        row = dict(row)
        row.setdefault("input", row.get("task_input") or row.get("text") or "")

        messages = []
        sys_msg = self.system(row)
        if sys_msg:
            messages.append({"role": "system", "content": sys_msg})

        messages.append({"role": "user", "content": self.user(row)})
        return messages, self.expects_json(row)