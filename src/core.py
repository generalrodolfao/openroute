"""
OpenRoute — Núcleo do roteador inteligente de LLMs.

Fluxo:
  1. Cache check → hit → retorna resposta cacheada
  2. Classifica query → escolhe provider + modelo
  3. Tenta provider primário
  4. Fallback se falhar
  5. Cache miss → armazena resposta
  6. Rastreia custo
"""

from typing import Optional

from src.config import DEFAULT_PROVIDER, DEFAULT_MODEL, FALLBACK_PROVIDER, FALLBACK_MODEL, LOCAL_FALLBACK
from src.cache import get_cache
from src.providers import PROVIDERS, LLMResponse
from src.router import select_route
from src.cost import CostEntry, get_tracker


class OpenRoute:
    def __init__(self):
        self.cache = get_cache()
        self.tracker = get_tracker()

    def _get_provider(self, provider_name: str):
        provider = PROVIDERS.get(provider_name)
        if not provider:
            raise ValueError(f"Provider desconhecido: {provider_name}")
        return provider

    def _try_provider(self, messages: list[dict], provider_name: str, model: str) -> Optional[LLMResponse]:
        try:
            provider = self._get_provider(provider_name)
            return provider(messages, model=model)
        except Exception as e:
            print(f"[openroute] Erro no provider {provider_name}/{model}: {e}")
            return None

    def complete(self, messages: list[dict], provider: Optional[str] = None,
                 model: Optional[str] = None, use_cache: bool = True,
                 allow_fallback: bool = True) -> LLMResponse:
        query = next((m["content"][:200] for m in messages if m["role"] == "user"), "")

        # 1. Cache check
        if use_cache:
            cached = self.cache.semantic_search(query)
            if cached:
                return LLMResponse(
                    content=cached["response"],
                    model=cached["metadata"].get("model", "cache"),
                    provider=cached["metadata"].get("provider", "cache"),
                    cost=0.0,
                )

        # 2. Roteamento
        if provider and model:
            target_provider, target_model = provider, model
        else:
            target_provider, target_model = select_route(query)

        # 3. Tentativa primária
        if self.tracker.exceeded():
            raise RuntimeError(f"Limite diário de custo excedido (${self.tracker.today():.2f}/${self.tracker.daily_limit})")

        response = self._try_provider(messages, target_provider, target_model)

        # 4. Fallback
        if response is None and allow_fallback:
            print(f"[openroute] Fallback para {FALLBACK_PROVIDER}/{FALLBACK_MODEL}")
            response = self._try_provider(messages, FALLBACK_PROVIDER, FALLBACK_MODEL)

        if response is None and LOCAL_FALLBACK:
            print(f"[openroute] Fallback local (ollama)")
            response = self._try_provider(messages, "ollama", "llama3")

        if response is None:
            raise RuntimeError("Todos os providers falharam")

        # 5. Cache
        if use_cache:
            self.cache.set(query, response.content, {
                "provider": response.provider,
                "model": response.model,
            })

        # 6. Custo
        self.tracker.add(CostEntry(
            provider=response.provider,
            model=response.model,
            cost=response.cost,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        ))

        return response

    def cost_summary(self) -> dict:
        return self.tracker.summary()

    def clear_cache(self):
        self.cache._store = {}
