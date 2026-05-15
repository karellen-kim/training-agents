import asyncio
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

aclient = AsyncAnthropic()


async def acall(prompt: str, system: str) -> str:
    msg = await aclient.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


async def vote_safety_check(code: str) -> bool:
    # Voting: 같은 작업을 다른 프롬프트로 3번 → 하나라도 위험 판정이면 reject
    perspectives = [
        "보안 엔지니어 관점에서 위험 식별",
        "악의적 사용자 관점에서 악용 경로 식별",
        "코드 리뷰어 관점에서 의심스러운 패턴 식별",
    ]
    results = await asyncio.gather(*[
        acall(f"코드:\n{code}\n\n'UNSAFE' 또는 'SAFE'만 답하라.", p)
        for p in perspectives
    ])
    print("[votes]", [r.strip() for r in results])
    return all("SAFE" in r.upper() for r in results)


if __name__ == "__main__":
    safe_code = """
def add(a: int, b: int) -> int:
    return a + b
"""

    risky_code = """
import os
def run(cmd: str):
    os.system(cmd)  # 사용자 입력을 그대로 셸에 전달
"""

    async def main():
        for label, code in [("safe", safe_code), ("risky", risky_code)]:
            verdict = await vote_safety_check(code)
            print(f"[{label}] all SAFE? {verdict}\n")

    asyncio.run(main())
