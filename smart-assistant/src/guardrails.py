
import re
import json
from typing import Tuple


class GuardrailSystem:
    MAX_INPUT_LENGTH = 500

    # Padrões de prompt injection (Aula 10)
    INJECTION_PATTERNS = [
        # Padrão 1: ignore/forget instructions
        (r"(ignore|esqueça|esquecer|desconsidere|forget)\s+.{0,30}(instructions?|rules?|prompts?|instruções|regras)",
         "tentativa de ignorar instruções"),

        # Padrão 2: you are now / act as
        (r"(you\s+are\s+now|você\s+é\s+agora|act\s+as|atue\s+como|pretend\s+to\s+be|finja\s+ser)\s+.{0,50}(without|sem)\s+(restriction|restrição|limit|limite|filter|filtro)",
         "tentativa de mudança de papel"),

        # Padrão 3: DAN / jailbreak explícito
        (r"\b(DAN|jailbreak|modo\s+deus|god\s+mode|developer\s+mode|modo\s+desenvolvedor)\b",
         "tentativa de jailbreak"),

        # Padrão 4: revelar system prompt
        (r"(reveal|show|display|mostrar?|exibir?|imprimir?|print)\s+.{0,30}(system\s*prompt|prompt\s+do\s+sistema|suas\s+instruções|your\s+instructions)",
         "tentativa de vazamento de prompt"),

        # Padrão 5: injeção via XML/tags falsas
        (r"<(system|admin|override|instrucao|instruction|root)\s*>",
         "injeção via tag XML"),

        # Padrão 6: override / admin commands
        (r"\b(override|bypass|contornar|admin\s+command|sudo|root\s+access)\b",
         "tentativa de override de sistema"),

        # Padrão 7: "na verdade você deve"
        (r"(na\s+verdade\s+(você|vc)\s+(deve|precisa|tem\s+que)|your\s+real\s+purpose\s+is|seu\s+verdadeiro\s+objetivo)",
         "redefinição de objetivo"),
    ]

    # Termos que NÃO devem aparecer na resposta
    OUTPUT_FORBIDDEN_TERMS = [
        "system prompt",
        "prompt do sistema",
        "minhas instruções",
        "my instructions",
        "ignore previous",
        "esqueça as instruções",
        "<system>",
        "<admin>",
    ]

    # Domínio permitido — palavras-chave de e-commerce/suporte
    DOMAIN_KEYWORDS = [
        "produto", "pedido", "entrega", "compra", "reembolso", "troca", "devolução",
        "pagamento", "frete", "estoque", "cliente", "suporte", "atendimento",
        "dúvida", "problema", "solicitação", "resposta", "obrigado", "agradece",
        "techstore", "protocolo", "prazo", "informação", "ajuda",
        # inglês também (para compatibilidade)
        "order", "product", "delivery", "refund", "payment", "support", "help"
    ]

    def validar_input(self, texto: str) -> Tuple[bool, str]:

        if not texto or not texto.strip():
            return False, "Entrada vazia"

        if len(texto) > self.MAX_INPUT_LENGTH:
            return False, f"Entrada muito longa ({len(texto)} chars, máximo {self.MAX_INPUT_LENGTH})"

        # Caracteres proibidos (tentativas de injeção estrutural)
        forbidden_chars = re.findall(r"[<>{}]", texto)
        if len(forbidden_chars) > 2:
            return False, f"Caracteres suspeitos detectados: {set(forbidden_chars)}"

        # Verifica padrões de injection
        texto_lower = texto.lower()
        for pattern, motivo in self.INJECTION_PATTERNS:
            if re.search(pattern, texto_lower, re.IGNORECASE):
                return False, f"Possível ataque detectado: {motivo}"

        return True, "ok"

    def validar_output(self, resposta: str) -> Tuple[bool, str]:
        if not resposta or not resposta.strip():
            return False, "Resposta vazia"

        resposta_lower = resposta.lower()

        # Verifica se não vazou termos do system prompt
        for termo in self.OUTPUT_FORBIDDEN_TERMS:
            if termo.lower() in resposta_lower:
                return False, f"Resposta contém termo proibido: '{termo}'"

        # Se for JSON, verifica se é válido
        if resposta.strip().startswith("{"):
            try:
                json.loads(resposta)
            except json.JSONDecodeError as e:
                return False, f"JSON inválido na resposta: {e}"

        return True, "ok"

    def esta_no_dominio(self, texto: str) -> bool:
        texto_lower = texto.lower()
        return any(kw in texto_lower for kw in self.DOMAIN_KEYWORDS)
