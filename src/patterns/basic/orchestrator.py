import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()


def llm_call(prompt: str, system: str = "", max_tokens: int = 1024) -> str:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _strip_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # ```json 또는 ``` 제거
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def orchestrate(task: str) -> str:
    # 1) 오케스트레이터가 하위 작업 목록을 동적으로 생성
    plan_json = llm_call(
        system=(
            "작업을 3~5개의 독립 하위 작업 JSON 배열로 분해. "
            "각 원소: {id, goal}. id는 짧은 영문 slug. "
            "코드 펜스나 설명 없이 순수 JSON 배열만 출력."
        ),
        prompt=task,
    )
    subtasks = json.loads(_strip_fence(plan_json))
    print(f"[plan] {len(subtasks)} subtasks: {[st['id'] for st in subtasks]}")

    # 2) 워커들이 하위 작업을 수행
    results = []
    for st in subtasks:
        print(f"[worker] {st['id']} ...", flush=True)
        out = llm_call(
            system="하위 작업을 정확히 수행하고 핵심만 3~6줄로 반환.",
            prompt=f"{st['goal']}",
            max_tokens=512,
        )
        results.append({"id": st["id"], "out": out})

    # 3) 합성
    print("[synth] ...", flush=True)
    return llm_call(
        system="하위 결과를 일관된 최종 산출물로 통합.",
        prompt=json.dumps(results, ensure_ascii=False),
    )


if __name__ == "__main__":
    task = "지속 가능한 패션 브랜드의 1주일 SNS 런칭 캠페인을 기획하라."
    final = orchestrate(task)
    print("=== 최종 산출물 ===")
    print(final)
