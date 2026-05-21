from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ClassificacaoSchema(BaseModel):
    """Resultado da Etapa 1: classificação da solicitação."""
    tipo: str = Field(description="reclamacao|duvida|elogio|sugestao")
    urgencia: str = Field(description="alta|media|baixa")
    tema: str = Field(description="Tema principal da solicitação")

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, v):
        opcoes = {"reclamacao", "duvida", "elogio", "sugestao"}
        v = v.lower().strip()
        if v not in opcoes:
            raise ValueError(f"tipo deve ser um de: {opcoes}")
        return v

    @field_validator("urgencia")
    @classmethod
    def urgencia_valida(cls, v):
        opcoes = {"alta", "media", "baixa"}
        v = v.lower().strip()
        if v not in opcoes:
            raise ValueError(f"urgencia deve ser um de: {opcoes}")
        return v


class ProcessamentoSchema(BaseModel):
    """Resultado da Etapa 2: processamento contextual."""
    dados_extraidos: dict = Field(description="Dados estruturados extraídos da solicitação")
    analise: str = Field(description="Análise detalhada do contexto")
    sentimento: Optional[str] = Field(default=None, description="positivo|negativo|neutro")
    acao_recomendada: str = Field(description="Próxima ação sugerida internamente")


class RespostaSchema(BaseModel):
    """Resultado da Etapa 3: resposta final formatada."""
    resposta: str = Field(description="Resposta completa ao cliente")
    confianca: str = Field(description="alta|media|baixa")
    acao_sugerida: str = Field(description="Ação que o cliente deve tomar")
    protocolo: Optional[str] = Field(default=None, description="Número de protocolo se aplicável")

    @field_validator("confianca")
    @classmethod
    def confianca_valida(cls, v):
        opcoes = {"alta", "media", "baixa"}
        v = v.lower().strip()
        if v not in opcoes:
            raise ValueError(f"confianca deve ser um de: {opcoes}")
        return v
