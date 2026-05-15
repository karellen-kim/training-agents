from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()


def augmented_llm(user_msg: str, tools: list, memory: list):
    # memory: 이전 turns / tools: 함수 스키마 리스트
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system="You are a precise assistant. Use tools when helpful.",
        messages=memory + [{"role": "user", "content": user_msg}],
        tools=tools,
    )
    return response


def run_tool(name: str, args: dict):
    if name == "add":
        return args["a"] + args["b"]
    if name == "multiply":
        return args["a"] * args["b"]
    raise ValueError(f"unknown tool: {name}")


if __name__ == "__main__":
    # 데모: add tool을 사용하는 agentic tool-use 루프
    tools = [
        {
            "name": "add",
            "description": "Add two integers and return the sum.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "multiply",
            "description": "Multiply two integers and return the product.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
        },
    ]

    # 두 도구를 모두 시연하려면 "(17 + 25) * 3 결과는?" 처럼 질문을 바꿔 보세요.
    user_question = "17 + 25는?"
    resp = augmented_llm(user_question, tools=tools, memory=[])

    messages = [
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": resp.content},
    ]

    while resp.stop_reason == "tool_use":
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"[tool] {block.name}({block.input}) -> {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="You are a precise assistant. Use tools when helpful.",
            messages=messages,
            tools=tools,
        )
        messages.append({"role": "assistant", "content": resp.content})

    print("stop_reason:", resp.stop_reason)
    for block in resp.content:
        if block.type == "text":
            print(block.text)
