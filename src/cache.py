"""
Cache semântico para respostas de LLMs.

Armazena embeddings das queries e retorna resposta cacheada
se a similaridade com uma query anterior for > threshold.
"""

import json
import time
import hashlib
from typing import Optional
import numpy as np
from numpy.linalg import norm

from src.config import CACHE_BACKEND, CACHE_TTL, SIMILARITY_THRESHOLD


def _cosine_sim(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    return float(np.dot(a_arr, b_arr) / (norm(a_arr) * norm(b_arr) + 1e-10))


def _embed(text: str) -> list[float]:
    text = text.lower().strip()
    ngrams = set()
    for n in range(2, 5):
        for i in range(len(text) - n + 1):
            ngrams.add(text[i:i + n])
    chars = sorted(ngrams)
    vec = [int(hashlib.md5(c.encode()).hexdigest(), 16) % 10000 / 10000.0 for c in chars]
    if not vec:
        return [0.0] * 64
    if len(vec) < 64:
        vec = vec * (64 // len(vec) + 1)
    return vec[:64]


class MemoryCache:
    def __init__(self, ttl: int = CACHE_TTL):
        self._store: dict[str, dict] = {}
        self._ttl = ttl

    def _key(self, query: str) -> str:
        return hashlib.sha256(query.encode()).hexdigest()

    def get(self, query: str) -> Optional[dict]:
        key = self._key(query)
        entry = self._store.get(key)
        if not entry:
            return None
        if time.time() - entry["ts"] > self._ttl:
            del self._store[key]
            return None
        return entry

    def set(self, query: str, response: str, metadata: dict | None = None):
        key = self._key(query)
        self._store[key] = {
            "query": query,
            "response": response,
            "metadata": metadata or {},
            "embedding": _embed(query),
            "ts": time.time(),
        }

    def semantic_search(self, query: str) -> Optional[dict]:
        q_emb = _embed(query)
        best_sim = 0.0
        best_entry = None
        now = time.time()
        to_delete = []
        for key, entry in self._store.items():
            if now - entry["ts"] > self._ttl:
                to_delete.append(key)
                continue
            sim = _cosine_sim(q_emb, entry["embedding"])
            if sim > best_sim:
                best_sim = sim
                best_entry = entry
        for k in to_delete:
            del self._store[k]
        if best_sim >= SIMILARITY_THRESHOLD:
            return best_entry
        return None


class RedisCache:
    def __init__(self, ttl: int = CACHE_TTL):
        import redis
        from src.config import REDIS_URL
        self._client = redis.from_url(REDIS_URL)
        self._ttl = ttl

    def _key(self, query: str) -> str:
        return f"openroute:cache:{hashlib.sha256(query.encode()).hexdigest()}"

    def get(self, query: str) -> Optional[dict]:
        data = self._client.get(self._key(query))
        if data:
            return json.loads(data)
        return None

    def set(self, query: str, response: str, metadata: dict | None = None):
        entry = {
            "query": query,
            "response": response,
            "metadata": metadata or {},
            "embedding": _embed(query),
        }
        self._client.setex(self._key(query), self._ttl, json.dumps(entry))

    def semantic_search(self, query: str) -> Optional[dict]:
        q_emb = _embed(query)
        best_sim = 0.0
        best_entry = None
        for key in self._client.scan_iter("openroute:cache:*"):
            data = self._client.get(key)
            if not data:
                continue
            entry = json.loads(data)
            sim = _cosine_sim(q_emb, entry["embedding"])
            if sim > best_sim:
                best_sim = sim
                best_entry = entry
        if best_sim >= SIMILARITY_THRESHOLD:
            return best_entry
        return None


def get_cache():
    if CACHE_BACKEND == "redis":
        return RedisCache()
    return MemoryCache()
