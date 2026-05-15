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


def classify(query: str) -> str:
    out = llm_call(
        system="분류기. 다음 중 하나로만 답: refund | technical | general",
        prompt=f"고객 문의: {query}\n\n카테고리만 출력.",
    )
    return out.strip().lower()


ROUTES = {
    "refund":    ("claude-haiku-4-5-20251001", "환불 정책에 따라 절차를 안내하라."),
    "technical": ("claude-sonnet-4-6",         "기술 지원 엔지니어처럼 단계별로 진단하라."),
    "general":   ("claude-haiku-4-5-20251001", "친절하게 응답하라."),
}


def route(query: str) -> str:
    category = classify(query)
    model, system = ROUTES.get(category, ROUTES["general"])
    print(f"[route] query={query!r} -> category={category} model={model}")
    msg = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": query}],
    )
    return msg.content[0].text


if __name__ == "__main__":
    queries = [
        "결제한 상품 환불 받고 싶어요.",
        "앱이 로그인 직후 계속 크래시 나는데 로그 어떻게 봐요?",
        "안녕하세요, 영업시간이 어떻게 되나요?",
    ]
    for q in queries:
        answer = route(q)
        print(f"\n--- 응답 ---\n{answer}\n")
