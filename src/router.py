"""
Roteador de queries — classifica o tipo de pergunta e escolhe o melhor modelo/provider.

Classes de roteamento:
  - simple: perguntas diretas → modelo barato (gpt-4o-mini)
  - reasoning: raciocínio lógico → modelo médio (gpt-4o)
  - creative: geração criativa → modelo premium (claude-3-sonnet)
  - code: código → modelo especializado (gpt-4o ou claude)
  - analysis: análise de dados → modelo com tool use
"""

ROUTING_RULES = {
    "simple": {
        "keywords": ["o que é", "quem é", "onde", "quando", "defina", "significado"],
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
    "code": {
        "keywords": ["código", "função", "implemente", "debug", "refatore",
                      "teste", "algoritmo", "sql", "python", "javascript"],
        "provider": "openai",
        "model": "gpt-4o-mini",
    },
    "analysis": {
        "keywords": ["análise", "analise", "métrica", "kpi", "dashboard", "relatório",
                      "estatística", "tendência", "comparativo"],
        "provider": "openai",
        "model": "gpt-4o",
    },
    "reasoning": {
        "keywords": ["por que", "como funciona", "explique", "compare", "diferença",
                      "qual a relação", "analise"],
        "provider": "openai",
        "model": "gpt-4o",
    },
    "creative": {
        "keywords": ["crie", "escreva", "gere", "invente", "história", "poema",
                      "roteiro", "título", "slogan"],
        "provider": "anthropic",
        "model": "claude-3-sonnet-20240229",
    },
}


def classify_query(query: str) -> str:
    q = query.lower()
    for category, rule in ROUTING_RULES.items():
        for kw in rule["keywords"]:
            if kw in q:
                return category
    return "simple"


def select_route(query: str) -> tuple[str, str]:
    category = classify_query(query)
    rule = ROUTING_RULES.get(category, ROUTING_RULES["simple"])
    return rule["provider"], rule["model"]
