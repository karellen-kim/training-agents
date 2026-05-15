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


def chain(input_text: str, prompts: list[str]) -> str:
    out = input_text
    for i, p in enumerate(prompts):
        out = llm_call(f"{p}\n\n<input>\n{out}\n</input>")
        print(f"\nStep {i}\nprompt: {p}\nout\n{out}")

        # 검증 게이트: 형식이 깨졌으면 중단
        if "<error>" in out.lower():
            raise RuntimeError(f"Step {i} failed: {out}")
    return out


if __name__ == "__main__":
    # 사용 예: 개요 → 검증 → 본문
    result = chain(
        "신년 마케팅 캠페인 주제: 친환경 패션",
        prompts=[
            "3문장 개요를 만든다.",
            "개요가 톤(미니멀, 진정성)에 맞는지 점검하고 다듬어라.",
            "개요를 200자 본문으로 확장하라.",
        ],
    )
    print(result)
