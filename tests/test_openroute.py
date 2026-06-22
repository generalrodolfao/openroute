import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import SIMILARITY_THRESHOLD, CACHE_TTL, COST_LIMIT_DAILY


class TestConfig:
    def test_defaults(self):
        assert SIMILARITY_THRESHOLD == 0.75
        assert CACHE_TTL == 3600
        assert COST_LIMIT_DAILY == 10.0


class TestCache:
    def test_memory_cache_set_get(self):
        from src.cache import MemoryCache
        c = MemoryCache(ttl=3600)
        c.set("query1", "resposta1")
        entry = c.get("query1")
        assert entry is not None
        assert entry["response"] == "resposta1"

    def test_memory_cache_miss(self):
        from src.cache import MemoryCache
        c = MemoryCache(ttl=3600)
        assert c.get("inexistente") is None

    def test_semantic_search_similar(self):
        from src.cache import MemoryCache
        c = MemoryCache(ttl=3600)
        c.set("O que é RAG?", "RAG é uma técnica...")
        result = c.semantic_search("Explique o que é RAG")
        assert result is not None
        assert "RAG" in result["response"]

    def test_semantic_search_different(self):
        from src.cache import MemoryCache
        c = MemoryCache(ttl=3600)
        c.set("Python é uma linguagem", "Python...")
        result = c.semantic_search("receita de bolo de chocolate")
        assert result is None

    def test_ttl_expiry(self):
        from src.cache import MemoryCache
        import time
        c = MemoryCache(ttl=1)
        c.set("query", "resposta")
        time.sleep(1.1)
        assert c.get("query") is None

    def test_embed_consistency(self):
        from src.cache import _embed
        e1 = _embed("mesma frase")
        e2 = _embed("mesma frase")
        assert e1 == e2

    def test_embed_length(self):
        from src.cache import _embed
        vec = _embed("teste")
        assert len(vec) == 64


class TestRouter:
    def test_classify_simple(self):
        from src.router import classify_query
        assert classify_query("O que é Python?") == "simple"

    def test_classify_reasoning(self):
        from src.router import classify_query
        assert classify_query("Por que o céu é azul?") == "reasoning"

    def test_classify_creative(self):
        from src.router import classify_query
        assert classify_query("Crie uma história sobre dados") == "creative"

    def test_classify_code(self):
        from src.router import classify_query
        assert classify_query("Crie uma função em Python") == "code"

    def test_classify_analysis(self):
        from src.router import classify_query
        assert classify_query("Analise essas métricas de vendas") == "analysis"

    def test_classify_fallback(self):
        from src.router import classify_query
        assert classify_query("aleatório sem keywords") == "simple"

    def test_select_route(self):
        from src.router import select_route
        provider, model = select_route("O que é RAG?")
        assert provider == "openai"
        assert model == "gpt-4o-mini"

    def test_select_route_creative(self):
        from src.router import select_route
        provider, model = select_route("Escreva um poema")
        assert provider == "anthropic"


class TestCost:
    def test_tracker_empty(self):
        from src.cost import CostTracker
        t = CostTracker(daily_limit=10)
        assert t.total() == 0.0
        assert not t.exceeded()

    def test_tracker_add(self):
        from src.cost import CostTracker, CostEntry
        t = CostTracker(daily_limit=10)
        t.add(CostEntry(provider="openai", model="gpt-4o", cost=0.5,
                         input_tokens=100, output_tokens=50))
        assert t.total() == 0.5
        assert not t.exceeded()

    def test_tracker_exceeded(self):
        from src.cost import CostTracker, CostEntry
        t = CostTracker(daily_limit=1)
        t.add(CostEntry(provider="openai", model="gpt-4o", cost=2.0,
                         input_tokens=100, output_tokens=50))
        assert t.exceeded()

    def test_tracker_summary(self):
        from src.cost import CostTracker, CostEntry
        t = CostTracker(daily_limit=10)
        t.add(CostEntry(provider="openai", model="gpt-4o", cost=1.0,
                         input_tokens=100, output_tokens=50))
        s = t.summary()
        assert s["total_cost"] == 1.0
        assert s["total_queries"] == 1


class TestProviders:
    def test_calc_cost(self):
        from src.providers import _calc_cost
        cost = _calc_cost("gpt-4o-mini", input_tokens=1000, output_tokens=500)
        assert cost == 1 * 0.00015 + 0.5 * 0.00060  # = 0.00045
        assert cost > 0

    def test_model_pricing_exists(self):
        from src.providers import MODEL_PRICING
        assert "gpt-4o-mini" in MODEL_PRICING
        assert "claude-3-haiku-20240307" in MODEL_PRICING

    def test_llm_response_dataclass(self):
        from src.providers import LLMResponse
        r = LLMResponse(content="teste", model="gpt-4o", provider="openai", cost=0.0)
        assert r.content == "teste"
        assert r.model == "gpt-4o"
