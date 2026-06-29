<h1 align="center">OpenRoute</h1>
<p align="center">
  <em>Roteador inteligente de LLMs — cache semântico, fallback automático, roteamento por tipo de query</em>
  <br/>
  <a href="https://github.com/generalrodolfao/openroute"><img src="https://img.shields.io/github/stars/generalrodolfao/openroute?style=flat-square&label=stars&color=F17405" /></a>
  <a href="https://github.com/generalrodolfao/openroute/actions"><img src="https://img.shields.io/github/actions/workflow/status/generalrodolfao/openroute/ci.yml?style=flat-square&label=CI&color=F17405" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-00154E?style=flat-square" /></a>
  <a href="https://www.python.org"><img src="https://img.shields.io/badge/python-3.11%2B-00154E?style=flat-square&logo=python&logoColor=F17405" /></a>
</p>

---

Roteia chamadas de LLM para o melhor modelo com base no **tipo da pergunta**, reduz custos com **cache semântico** e garante resiliência com **fallback automático** entre provedores.

---

## Por que OpenRoute?

| Problema | Solução OpenRoute |
|---|---|
| Toda query vai pro modelo mais caro | Classifica a query e roteia pro modelo certo: simples → mini, complexo → pro |
| Queries repetidas consomem crédito | Cache semântico: queries similares retornam do cache sem chamar API |
| API fora do ar quebra o pipeline | Fallback automático: OpenAI → Anthropic → Ollama (local) |
| Custo invisível até o fim do mês | Rastreio de custo por query/modelo/provider + limite diário configurável |

OpenRoute **não** é um proxy universal como OpenRouter.ai ou LiteLLM. É um **roteador inteligente** que decide *qual* modelo usar baseado no *conteúdo* da query, não apenas no preço.

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Roteamento inteligente** | Classifica a query e escolhe o provedor/modelo ideal |
| **Cache semântico** | Retorna respostas similares sem chamar a API (threshold configurável) |
| **Fallback automático** | Se o provider primário falha, tenta secundário → local |
| **Rastreio de custo** | Controle granular por query, modelo, provider e período |
| **Limite diário** | Interrompe automaticamente se o custo do dia exceder o limite |
| **Múltiplos providers** | OpenAI, Anthropic, Ollama (com fácil extensão) |

---

## Roteamento

| Categoria | Exemplos | Provider | Modelo | Custo |
|---|---|---|---|---|
| `simple` | "O que é X?" | OpenAI | gpt-4o-mini | Baixo |
| `reasoning` | "Por que X funciona?" | OpenAI | gpt-4o | Médio |
| `creative` | "Escreva um poema" | Anthropic | claude-3-sonnet | Alto |
| `code` | "Crie uma função" | OpenAI | gpt-4o-mini | Baixo |
| `analysis` | "Analise esses dados" | OpenAI | gpt-4o | Médio |

---

## Comparação com alternativas

| | OpenRoute | OpenRouter.ai | LiteLLM |
|---|---|---|---|
| Roteamento por conteúdo | ✅ | ❌ (preço) | ❌ (preço) |
| Cache semântico | ✅ | ❌ | ❌ |
| Fallback automático | ✅ | ✅ | ✅ |
| Rastreio de custo | ✅ | ✅ | ✅ |
| Self-hosted | ✅ | ❌ (SaaS) | ✅ |
| Ollama (local) | ✅ | ❌ | ✅ |

---

## Quickstart

```bash
git clone https://github.com/generalrodolfao/openroute.git
cd openroute

cp .env.example .env
# Edite com suas chaves de API

pip install -r requirements.txt
python examples/quickstart.py
```

## Uso programático

```python
from src.core import OpenRoute

router = OpenRoute()

# Roteamento automático
resp = router.complete([
    {"role": "user", "content": "Explique RAG em produção"}
])
print(resp.content)

# Forçar provider/modelo
resp = router.complete(
    messages=[{"role": "user", "content": "Crie uma função"}],
    provider="anthropic",
    model="claude-3-sonnet-20240229",
)

# Cache desabilitado
resp = router.complete(messages=[...], use_cache=False)

# Ver custos
print(router.cost_summary())
```

---

## Arquitetura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Query     │────→│   Classify   │────→│   Route     │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                    ┌───────────────────────────┼───────────┐
                    ▼                           ▼           ▼
            ┌──────────────┐           ┌──────────────┐    ┌──────────┐
            │   Cache      │◄──────────│   Provider   │    │  Cost    │
            │   Check      │  (miss→)  │   Call       │    │  Track   │
            └──────┬───────┘           └──────┬───────┘    └──────────┘
                   │                          │
                   │ (hit→retorna)            ▼
                   │                  ┌──────────────┐
                   │                  │   Fallback   │
                   │                  │   (se falhar) │
                   │                  └──────┬───────┘
                   │                         │
                   └─────────────────────────┘
                                    │
                                    ▼
                            ┌──────────────┐
                            │   Cache      │
                            │   Store      │
                            └──────────────┘
```

---

## Testes

```bash
pytest tests/ -v
```

---

<p align="center">
  <a href="https://github.com/generalrodolfao"><img src="https://img.shields.io/badge/github-generalrodolfao-00154E?style=flat-square&logo=github&logoColor=F17405" /></a>
  <a href="https://linkedin.com/in/generalrodolfao"><img src="https://img.shields.io/badge/LinkedIn-generalrodolfao-00154E?style=flat-square&logo=linkedin&logoColor=F17405" /></a>
  <a href="mailto:rodolfo@dtsqd.com"><img src="https://img.shields.io/badge/-rodolfo@dtsqd.com-00154E?style=flat-square&logo=gmail&logoColor=F17405" /></a>
</p>
