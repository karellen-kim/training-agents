from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()


def llm_call(prompt: str, system: str = "") -> str:
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def eval_optimize(task: str, max_iters: int = 3) -> str:
    draft = llm_call(system="초안을 작성.", prompt=task)

    for i in range(max_iters):
        critique = llm_call(
            system=("엄격한 평가자. 기준: 명료성, 사실성, 톤. "
                    "마지막 줄에 PASS 또는 REVISE만 출력."),
            prompt=f"<task>{task}</task>\n<draft>{draft}</draft>",
        )
        if critique.strip().splitlines()[-1].strip() == "PASS":
            return draft

        draft = llm_call(
            system="피드백을 반영해 다시 작성.",
            prompt=f"<draft>{draft}</draft>\n<critique>{critique}</critique>",
        )
        print(f"draft={draft}")
    return draft  # 한도 도달: 마지막 draft 반환


if __name__ == "__main__":
    task = "지속 가능한 패션 브랜드의 신년 캠페인 카피를 200자 이내로 작성."
    final = eval_optimize(task)
    print("=== 최종 결과 ===")
    print(final)
