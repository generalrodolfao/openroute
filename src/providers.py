"""
Wrappers para provedores de LLM.

Cada provider expõe a mesma interface:
  - complete(messages) -> (content, cost, tokens)
"""

from dataclasses import dataclass
from typing import Optional

from src.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, OLLAMA_BASE_URL


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    cost: float
    input_tokens: int = 0
    output_tokens: int = 0


MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.00060},
    "gpt-4o": {"input": 0.00250, "output": 0.01000},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    "claude-3-sonnet-20240229": {"input": 0.00300, "output": 0.01500},
    "claude-3-opus-20240229": {"input": 0.01500, "output": 0.07500},
}


def _calc_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING.get(model, {"input": 0.001, "output": 0.002})
    return (input_tokens / 1000 * pricing["input"]
            + output_tokens / 1000 * pricing["output"])


def openai_complete(messages: list[dict], model: str = "gpt-4o-mini", **kwargs) -> LLMResponse:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
    choice = response.choices[0]
    usage = response.usage
    cost = _calc_cost(model, usage.prompt_tokens, usage.completion_tokens)

    return LLMResponse(
        content=choice.message.content or "",
        model=model,
        provider="openai",
        cost=cost,
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
    )


def anthropic_complete(messages: list[dict], model: str = "claude-3-haiku-20240307", **kwargs) -> LLMResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    system = None
    filtered = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        else:
            filtered.append({"role": m["role"], "content": m["content"]})

    response = client.messages.create(
        model=model,
        system=system,
        messages=filtered,
        **kwargs,
    )
    cost = _calc_cost(model, response.usage.input_tokens, response.usage.output_tokens)

    return LLMResponse(
        content=response.content[0].text,
        model=model,
        provider="anthropic",
        cost=cost,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


def ollama_complete(messages: list[dict], model: str = "llama3", **kwargs) -> LLMResponse:
    from openai import OpenAI

    client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
    content = response.choices[0].message.content or ""

    return LLMResponse(
        content=content,
        model=model,
        provider="ollama",
        cost=0.0,
        input_tokens=0,
        output_tokens=0,
    )


PROVIDERS = {
    "openai": openai_complete,
    "anthropic": anthropic_complete,
    "ollama": ollama_complete,
}
