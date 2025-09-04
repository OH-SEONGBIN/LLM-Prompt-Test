class StructuredJSONSet:
    name = "structured"

    SYS = (
        "너는 데이터 정확성을 최우선으로 하는 어시스턴트다. "
        "사실만 답하고, 요구한 JSON 스키마를 반드시 지켜."
    )

    def system(self, row) -> str | None:
        return self.SYS

    def expects_json(self, row) -> bool:
        return True

    def temperature(self, row) -> float:
        # 재현성 위해 낮춤
        return 0.2

    def user(self, row) -> str:
        task, text = row["task"], str(row["input"])
        if task == "summarization":
            max_len = int(row.get("max_len") or 200)
            key_terms = [k.strip() for k in str(row.get("key_terms") or "").split("|") if k.strip()]
            key_part = f' 필수키("{", ".join(key_terms)}") 포함 노력,' if key_terms else ""
            return (
                f"{max_len}자 이내 한국어 요약을 반환해.{key_part} 반드시 JSON으로만 답해.\n"
                f'스키마: {{"summary":"string"}}\n\n텍스트:\n{text}'
            )
        if task == "classification":
            return (
                "문장을 감성으로 분류해. 반드시 JSON으로만 답해.\n"
                '스키마: {"label":"positive|negative"}\n\n'
                f"문장:\n{text}"
            )
        if task == "extraction":
            return (
                "텍스트에서 이름, 이메일, 전화번호를 추출해. 반드시 JSON으로만 답해.\n"
                '스키마: {"name":"string","email":"string","phone":"string"}\n\n'
                f"텍스트:\n{text}"
            )
        raise ValueError(f"Unknown task: {task}")

    # ✅ 반드시 인스턴스 메서드로!
    def build(self, row):
        """
        prompt_bench 가 호출하는 진입점.
        (messages, json_mode_bool) 반환
        """
        row = dict(row)
        row.setdefault("input", row.get("task_input") or row.get("text") or "")

        messages = []
        sys_msg = self.system(row)
        if sys_msg:
            messages.append({"role": "system", "content": sys_msg})

        messages.append({"role": "user", "content": self.user(row)})
        return messages, self.expects_json(row)