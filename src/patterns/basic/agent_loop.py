from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()


TOOLS = [
    {
        "name": "read_file",
        "description": "파일 내용을 읽는다. 주니어 개발자에게 설명하듯 명확히.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    # ... 다른 도구들
]


def run_tool(name: str, args: dict) -> str:
    if name == "read_file":
        with open(args["path"]) as f:
            return f.read()
    raise ValueError(f"unknown tool: {name}")


def agent(goal: str, max_steps: int = 10):
    messages = [{"role": "user", "content": goal}]

    for step in range(max_steps):
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        if resp.stop_reason == "end_turn":
            return resp.content[0].text

        # 도구 호출 처리
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"[step {step}] {block.name}({block.input})")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})

    raise RuntimeError("max_steps reached without completion")


if __name__ == "__main__":
    answer = agent("pyproject.toml을 읽고 의존성 목록을 한 줄씩 정리해줘.")
    print("\n=== 최종 응답 ===")
    print(answer)
