"""
Quickstart — OpenRoute

Uso:
  python examples/quickstart.py
"""

from src.core import OpenRoute

router = OpenRoute()

queries = [
    {"role": "user", "content": "O que é RAG em sistemas de IA?"},
    {"role": "user", "content": "Escreva um poema sobre dados"},
    {"role": "user", "content": "Crie uma função Python que calcula fibonacci"},
    {"role": "user", "content": "Por que devemos usar cache semântico em LLMs?"},
]

for msg in queries:
    print(f"\n{'='*60}")
    print(f"Query: {msg['content']}")
    try:
        response = router.complete([msg])
        print(f"Provider: {response.provider}/{response.model}")
        print(f"Custo: ${response.cost:.6f}")
        print(f"Resposta: {response.content[:150]}...")
    except Exception as e:
        print(f"Erro: {e}")

print(f"\n{'='*60}")
print("Resumo de custos:", router.cost_summary())
