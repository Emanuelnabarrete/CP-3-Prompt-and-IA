"""
chain.py — Pipeline Multi-Etapa (Aula 09)

3 etapas com lógica condicional:
  Etapa 1: Classificar — tipo, urgência, tema
  Etapa 2: Processar   — lógica CONDICIONAL baseada no tipo da etapa 1
  Etapa 3: Responder   — formatar resposta final com framework CRISPE
"""

import json
import re
import random
import string
from typing import Optional

from src.llm_client import LLMClient
from src.schemas import ClassificacaoSchema, ProcessamentoSchema, RespostaSchema
from src.prompts import (
    carregar_system_prompt,
    PROMPT_CLASSIFICAR,
    PROMPT_RESPONDER,
    get_prompt_processar,
)


def _extrair_json(texto: str) -> dict:
    """
    Extrai JSON de uma resposta do LLM, lidando com markdown e texto extra.
    """
    # Tenta diretamente
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    # Remove blocos ```json ... ```
    limpo = re.sub(r"```(?:json)?\s*", "", texto).replace("```", "").strip()
    try:
        return json.loads(limpo)
    except json.JSONDecodeError:
        pass

    # Tenta encontrar o primeiro objeto JSON no texto
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {}


def _gerar_protocolo() -> str:
    sufixo = "".join(random.choices(string.digits, k=5))
    return f"TS-{sufixo}"


class AssistantChain:
    """
    Pipeline condicional de 3 etapas para processamento de solicitações.
    CP03 — Smart Assistant | TechStore Support
    """

    FALLBACK_CLASSIFICACAO = {
        "tipo": "duvida",
        "urgencia": "media",
        "tema": "solicitação geral"
    }

    def __init__(self):
        self.client = LLMClient()
        self.system_prompt = carregar_system_prompt()

    # ─────────────────────────────────────────────
    # ETAPA 1: Classificar
    # ─────────────────────────────────────────────
    def etapa1_classificar(self, texto: str) -> ClassificacaoSchema:
        """
        Classifica a solicitação do usuário.
        Retorna tipo, urgência e tema validados com Pydantic.
        """
        prompt = PROMPT_CLASSIFICAR.format(texto=texto)

        response = self.client.chat(
            prompt=prompt,
            system=self.system_prompt,
            temperature=0.1,
            max_tokens=150
        )

        dados = _extrair_json(response["answer"])

        # Fallback se JSON inválido ou campos ausentes
        if not dados or "tipo" not in dados:
            dados = self.FALLBACK_CLASSIFICACAO.copy()

        try:
            return ClassificacaoSchema(**dados)
        except Exception:
            return ClassificacaoSchema(**self.FALLBACK_CLASSIFICACAO)

    # ─────────────────────────────────────────────
    # ETAPA 2: Processar (CONDICIONAL)
    # ─────────────────────────────────────────────
    def etapa2_processar(self, texto: str, classificacao: ClassificacaoSchema) -> ProcessamentoSchema:
        """
        Processa a solicitação de forma CONDICIONAL baseada no tipo da etapa 1:
        - reclamacao → extrai produto + problema
        - duvida     → gera resposta informativa
        - elogio     → agradece e registra
        - sugestao   → registra sugestão
        """
        # Template selecionado condicionalmente pelo tipo
        template = get_prompt_processar(classificacao.tipo)

        prompt = template.format(
            tipo=classificacao.tipo,
            urgencia=classificacao.urgencia,
            tema=classificacao.tema,
            texto=texto
        )

        response = self.client.chat(
            prompt=prompt,
            system=self.system_prompt,
            temperature=0.2,
            max_tokens=400
        )

        dados = _extrair_json(response["answer"])

        # Fallback
        if not dados or "dados_extraidos" not in dados:
            dados = {
                "dados_extraidos": {"info": texto[:100]},
                "analise": "Não foi possível processar completamente.",
                "sentimento": "neutro",
                "acao_recomendada": "revisao_manual"
            }

        try:
            return ProcessamentoSchema(**dados)
        except Exception as e:
            return ProcessamentoSchema(
                dados_extraidos={"info": texto[:100]},
                analise=str(e),
                sentimento="neutro",
                acao_recomendada="revisao_manual"
            )

    # ─────────────────────────────────────────────
    # ETAPA 3: Responder
    # ─────────────────────────────────────────────
    def etapa3_responder(self, texto: str, classificacao: ClassificacaoSchema,
                         processamento: ProcessamentoSchema) -> RespostaSchema:
        """
        Gera a resposta final usando o framework CRISPE.
        """
        prompt = PROMPT_RESPONDER.format(
            tipo=classificacao.tipo,
            urgencia=classificacao.urgencia,
            analise=processamento.analise,
            acao_recomendada=processamento.acao_recomendada,
            dados_extraidos=json.dumps(processamento.dados_extraidos, ensure_ascii=False),
            texto=texto
        )

        response = self.client.chat(
            prompt=prompt,
            system=self.system_prompt,
            temperature=0.4,
            max_tokens=512
        )

        dados = _extrair_json(response["answer"])

        if not dados or "resposta" not in dados:
            dados = {
                "resposta": "Obrigado pelo contato! Nossa equipe analisará sua solicitação em breve.",
                "confianca": "baixa",
                "acao_sugerida": "Aguarde retorno em até 48h",
                "protocolo": _gerar_protocolo()
            }

        # Garante protocolo
        if not dados.get("protocolo") or dados["protocolo"] == "null":
            dados["protocolo"] = _gerar_protocolo()

        try:
            return RespostaSchema(**dados)
        except Exception:
            return RespostaSchema(
                resposta=dados.get("resposta", "Contato registrado."),
                confianca="baixa",
                acao_sugerida="Aguarde retorno",
                protocolo=_gerar_protocolo()
            )

    # ─────────────────────────────────────────────
    # Pipeline completo
    # ─────────────────────────────────────────────
    def processar(self, texto: str) -> dict:
        """
        Executa o pipeline completo e retorna todas as etapas.
        """
        etapa1 = self.etapa1_classificar(texto)
        etapa2 = self.etapa2_processar(texto, etapa1)
        etapa3 = self.etapa3_responder(texto, etapa1, etapa2)

        return {
            "input": texto,
            "etapa1_classificacao": etapa1.model_dump(),
            "etapa2_processamento": etapa2.model_dump(),
            "etapa3_resposta": etapa3.model_dump(),
        }
