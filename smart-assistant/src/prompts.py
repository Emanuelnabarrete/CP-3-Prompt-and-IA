"""
prompts.py — Frameworks Profissionais de Prompt Engineering (Aula 11)

Padrões aplicados:
- Persona Pattern: assistente com identidade definida (Ana, analista sênior de CX)
- Template Pattern: placeholders dinâmicos por tipo de solicitação
- Recipe Pattern: instruções passo a passo estruturadas
- CRISPE: Capacity, Role, Insight, Statement, Personality, Experiment
"""

import os


def carregar_system_prompt() -> str:
    """Carrega o system prompt defensivo do arquivo."""
    caminho = os.path.join(os.path.dirname(__file__), "..", "prompts", "system_prompt.txt")
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────────
# TEMPLATE PATTERN — Etapa 1: Classificação
# ─────────────────────────────────────────────
PROMPT_CLASSIFICAR = """
<tarefa>CLASSIFICAÇÃO DE SOLICITAÇÃO</tarefa>

<instrucao>
Analise a solicitação do cliente e classifique-a seguindo EXATAMENTE o formato JSON abaixo.
NÃO adicione explicações fora do JSON.
</instrucao>

<solicitacao_cliente>
{texto}
</solicitacao_cliente>

<formato_obrigatorio>
Responda APENAS com JSON válido, sem markdown, sem ```json, somente o objeto:
{{
  "tipo": "<reclamacao|duvida|elogio|sugestao>",
  "urgencia": "<alta|media|baixa>",
  "tema": "<tema principal em até 5 palavras>"
}}
</formato_obrigatorio>

<regras>
- tipo "reclamacao": cliente insatisfeito, produto com defeito, problema, erro
- tipo "duvida": pergunta, como funciona, quero saber, qual é
- tipo "elogio": ótimo, excelente, adorei, parabéns, muito bom
- tipo "sugestao": poderia ter, seria melhor, sugestão, ideia
- urgencia "alta": palavra urgente, prazo, hoje, problema crítico, não funciona
- urgencia "media": em breve, quando possível, quero resolver
- urgencia "baixa": curiosidade, elogio, sugestão sem prazo
</regras>
"""

# ─────────────────────────────────────────────
# RECIPE PATTERN — Etapa 2: Processamento
# ─────────────────────────────────────────────
PROMPT_PROCESSAR_RECLAMACAO = """
<tarefa>PROCESSAMENTO DE RECLAMAÇÃO</tarefa>

<contexto_classificacao>
Tipo: {tipo} | Urgência: {urgencia} | Tema: {tema}
</contexto_classificacao>

<solicitacao_original>
{texto}
</solicitacao_original>

<receita_processamento>
Siga OBRIGATORIAMENTE estas etapas:
1. Identifique o produto ou serviço mencionado
2. Extraia o problema específico relatado
3. Avalie o impacto para o cliente
4. Determine a ação interna necessária
5. Classifique o sentimento (negativo/muito_negativo)
</receita_processamento>

<formato_obrigatorio>
Responda APENAS com JSON válido:
{{
  "dados_extraidos": {{
    "produto": "<produto ou servico mencionado>",
    "problema": "<descrição do problema>",
    "impacto": "<impacto para o cliente>"
  }},
  "analise": "<análise do contexto em 1-2 frases>",
  "sentimento": "negativo",
  "acao_recomendada": "<ação interna: reembolso|troca|escalamento|investigacao>"
}}
</formato_obrigatorio>
"""

PROMPT_PROCESSAR_DUVIDA = """
<tarefa>PROCESSAMENTO DE DÚVIDA</tarefa>

<contexto_classificacao>
Tipo: {tipo} | Urgência: {urgencia} | Tema: {tema}
</contexto_classificacao>

<solicitacao_original>
{texto}
</solicitacao_original>

<receita_processamento>
Siga OBRIGATORIAMENTE estas etapas:
1. Identifique a dúvida principal
2. Identifique o produto/serviço relacionado se mencionado
3. Determine as informações necessárias para responder
4. Estime a complexidade da resposta (simples/moderada/complexa)
</receita_processamento>

<formato_obrigatorio>
Responda APENAS com JSON válido:
{{
  "dados_extraidos": {{
    "duvida_principal": "<dúvida em uma frase>",
    "produto_relacionado": "<produto ou 'geral'>",
    "complexidade": "<simples|moderada|complexa>"
  }},
  "analise": "<análise do que o cliente precisa saber>",
  "sentimento": "neutro",
  "acao_recomendada": "responder_informacao"
}}
</formato_obrigatorio>
"""

PROMPT_PROCESSAR_ELOGIO = """
<tarefa>PROCESSAMENTO DE ELOGIO</tarefa>

<contexto_classificacao>
Tipo: {tipo} | Urgência: {urgencia} | Tema: {tema}
</contexto_classificacao>

<solicitacao_original>
{texto}
</solicitacao_original>

<receita_processamento>
Siga OBRIGATORIAMENTE estas etapas:
1. Identifique o que foi elogiado (produto, atendimento, entrega, etc)
2. Extraia aspectos positivos mencionados
3. Identifique oportunidade de fidelização
</receita_processamento>

<formato_obrigatorio>
Responda APENAS com JSON válido:
{{
  "dados_extraidos": {{
    "aspecto_elogiado": "<o que foi elogiado>",
    "pontos_positivos": ["<ponto 1>", "<ponto 2>"]
  }},
  "analise": "<breve análise do elogio>",
  "sentimento": "positivo",
  "acao_recomendada": "agradecer_e_fidelizar"
}}
</formato_obrigatorio>
"""

PROMPT_PROCESSAR_SUGESTAO = """
<tarefa>PROCESSAMENTO DE SUGESTÃO</tarefa>

<contexto_classificacao>
Tipo: {tipo} | Urgência: {urgencia} | Tema: {tema}
</contexto_classificacao>

<solicitacao_original>
{texto}
</solicitacao_original>

<formato_obrigatorio>
Responda APENAS com JSON válido:
{{
  "dados_extraidos": {{
    "sugestao_principal": "<sugestão resumida>",
    "area_impactada": "<produto|entrega|atendimento|site|outro>"
  }},
  "analise": "<avaliação da viabilidade da sugestão>",
  "sentimento": "neutro",
  "acao_recomendada": "registrar_sugestao"
}}
</formato_obrigatorio>
"""

# ─────────────────────────────────────────────
# CRISPE PATTERN — Etapa 3: Resposta Final
# ─────────────────────────────────────────────
PROMPT_RESPONDER = """
<crispe>
  <capacity>Especialista em atendimento ao cliente com 12 anos de experiência em e-commerce</capacity>
  <role>Ana, Analista Sênior de Customer Experience da TechStore</role>
  <insight>
    Classificação: {tipo} | Urgência: {urgencia}
    Análise: {analise}
    Ação recomendada: {acao_recomendada}
    Dados: {dados_extraidos}
  </insight>
  <statement>
    Gere uma resposta profissional, empática e objetiva para o cliente.
    A resposta deve ser em português brasileiro.
    Para reclamações: reconheça o problema e ofereça solução.
    Para dúvidas: responda de forma clara e completa.
    Para elogios: agradeça de forma genuína e incentive retorno.
    Para sugestões: agradeça e informe que será avaliada.
  </statement>
  <personality>Tom empático, profissional, direto. Nunca use jargões técnicos.</personality>
  <experiment>Gere a melhor resposta possível para fidelizar o cliente.</experiment>
</crispe>

<solicitacao_original>
{texto}
</solicitacao_original>

<formato_obrigatorio>
Responda APENAS com JSON válido:
{{
  "resposta": "<resposta completa ao cliente em português>",
  "confianca": "<alta|media|baixa>",
  "acao_sugerida": "<o que o cliente deve fazer a seguir>",
  "protocolo": "<gere um código no formato TS-XXXXX ou null>"
}}
</formato_obrigatorio>
"""


def get_prompt_processar(tipo: str) -> str:
    """Retorna o template correto de processamento baseado no tipo."""
    mapa = {
        "reclamacao": PROMPT_PROCESSAR_RECLAMACAO,
        "duvida": PROMPT_PROCESSAR_DUVIDA,
        "elogio": PROMPT_PROCESSAR_ELOGIO,
        "sugestao": PROMPT_PROCESSAR_SUGESTAO,
    }
    return mapa.get(tipo, PROMPT_PROCESSAR_DUVIDA)
