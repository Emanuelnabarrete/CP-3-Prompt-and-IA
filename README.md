
## **Checkpoint 03 — Prompt Engineering & AI | FIAP | Grupo 2**

Assistente inteligente de suporte ao cliente da TechStore, construído com pipeline de 3 etapas (prompt chaining), structured output via Pydantic, guardrails de segurança e frameworks profissionais de prompt engineering.

---

## 👥 Integrantes

| Nome | RM |
|---|---|
| Emanuel Nabarrete | 566931 |
| Luiz Eduardo | 567417 |
| Eduardo Luiz | 567662 |
| Miguel Bezerra | 566763 |
| Lucas Mota | 566670 |

---

## 🏗 Arquitetura

```
Input usuário
    ↓
🛡 Input Guard (guardrails.py)
    ↓
🔗 Etapa 1: Classificar (chain.py) → ClassificacaoSchema (Pydantic)
    ↓
🔗 Etapa 2: Processar — CONDICIONAL por tipo (chain.py) → ProcessamentoSchema
    ↓
🔗 Etapa 3: Responder com CRISPE (chain.py) → RespostaSchema
    ↓
🛡 Output Guard (guardrails.py)
    ↓
Resposta JSON validada
```

---

## ⚙️ Stack Técnica

- **Python** 3.10+
- **LLM**: Ollama API local (`gpt-oss:120b`)
- **Validação**: `pydantic>=2.0`
- **Tokens**: `tiktoken`
- **Análise**: `pandas` + `matplotlib`
- **Segurança**: regex patterns customizados (7 padrões de injection)

---

## 🚀 Instalação e Execução

### 1. Pré-requisitos
- [Ollama](https://ollama.ai) instalado e rodando
- Modelo `gpt-oss:120b` disponível: `ollama pull gpt-oss:120b`

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite .env se necessário (padrão: localhost:11434)
```

### 4. Rodar

**Modo interativo** (conversa com o assistente):
```bash
python main.py
```

**Modo avaliação** (roda dataset de testes e gera métricas):
```bash
python main.py --avaliar
```

---

## 💬 Exemplos de Uso

```
Você: Meu produto chegou com defeito, a tela está quebrada!
──────────────────────────────────────────────────────────
📋 Tipo: RECLAMACAO | Urgência: ALTA | Protocolo: TS-84721
💬 Assistente: Olá! Lamentamos muito pelo inconveniente...
✅ Ação: Entre em contato pelo chat com o protocolo TS-84721
🎯 Confiança: ALTA
```

---

## 📁 Estrutura de Pastas

```
smart-assistant/
├── main.py                    # Ponto de entrada
├── requirements.txt
├── .env.example
├── src/
│   ├── llm_client.py          # Conexão Ollama (evoluído do CP02)
│   ├── guardrails.py          # 3 camadas de segurança
│   ├── chain.py               # Pipeline multi-etapa condicional
│   ├── schemas.py             # Pydantic schemas (3 etapas)
│   ├── prompts.py             # Templates + frameworks (CRISPE, Recipe, Persona)
│   └── evaluator.py           # Avaliação automática (5 métricas)
├── prompts/
│   ├── system_prompt.txt      # System prompt defensivo (v3 final)
│   └── versions/
│       ├── v1.txt             # Versão inicial
│       ├── v2.txt             # Com persona e regras básicas
│       └── v3.txt             # Final otimizada (CRISPE + XML tags)
├── data/
│   ├── test_dataset.json      # 16 casos de teste
│   └── attack_dataset.json    # 8 ataques de injection
├── output/
│   ├── eval_results.csv
│   └── graficos/
└── docs/
    └── CP03_Grupo2.pdf
```

---

## 🛡 Guardrails

- **Input Guard**: bloqueia entradas > 500 chars, caracteres proibidos e 7 padrões de injection
- **System Prompt Defensivo**: persona detalhada, 8 regras críticas, separação dados/instruções via XML tags
- **Output Guard**: verifica termos proibidos, valida JSON, confirma domínio

---

## 📊 Métricas de Avaliação

| Métrica | Descrição |
|---|---|
| Acurácia de Classificação | % de tipos classificados corretamente |
| Taxa de JSON Válido | % de respostas validadas por Pydantic |
| Taxa de Bloqueio | % de ataques corretamente bloqueados |
| Taxa de Falso Positivo | % de legítimas erroneamente bloqueadas |
| Consistência | Mesma entrada 3x → mesma classificação |

