

import sys
import json
from src.chain import AssistantChain
from src.guardrails import GuardrailSystem


def modo_interativo():
    print("")
    print(" TechStore Smart Assistant")
    print("  Checkpoint 03 — FIAP | Grupo 2")
    print("=" * 60)
    print("Digite 'sair' para encerrar.\n")

    chain = AssistantChain()
    guardrails = GuardrailSystem()

    while True:
        try:
            entrada = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\Encerrando assistente.")
            break

        if not entrada:
            continue

        if entrada.lower() in ("sair", "exit", "quit"):
            print("Encerrando assistente.")
            break

        # ── Etapa: Input Guard ──────────────────
        is_safe, motivo = guardrails.validar_input(entrada)
        if not is_safe:
            print(f"\n🛡 [BLOQUEADO] {motivo}\n")
            continue

        print("\nProcessando...")

        # ── Pipeline: 3 etapas ──────────────────
        resultado = chain.processar(entrada)

        # ── Output Guard ────────────────────────
        resposta_texto = resultado["etapa3_resposta"]["resposta"]
        is_safe_out, motivo_out = guardrails.validar_output(resposta_texto)
        if not is_safe_out:
            print(f"🛡 [OUTPUT BLOQUEADO] {motivo_out}")
            resposta_texto = "Desculpe, não consigo processar esta solicitação agora."

        # ── Exibição ────────────────────────────
        tipo = resultado["etapa1_classificacao"]["tipo"].upper()
        urgencia = resultado["etapa1_classificacao"]["urgencia"].upper()
        protocolo = resultado["etapa3_resposta"].get("protocolo", "N/A")
        confianca = resultado["etapa3_resposta"]["confianca"].upper()

        print(f"\nTipo: {tipo} | Urgência: {urgencia} | Protocolo: {protocolo}")
        print("")
        print(f"ssistente: {resposta_texto}")
        print("")
        print(f"Ação: {resultado['etapa3_resposta']['acao_sugerida']}")
        print("")
        print(f"Confiança: {confianca}")


def modo_avaliacao():

    print("\nTechStore Smart Assistant — Modo Avaliação\n")


    from src.evaluator import Evaluator
    evaluator = Evaluator()
    resultados = evaluator.rodar_avaliacao_completa()

    print("\n" + "=" * 60)
    print(" RESULTADO FINAL DAS MÉTRICAS")
    print("=" * 60)

    metricas = resultados["metricas_resumo"]


    print("\nRelatórios salvos/")
    print("Gráficos salvos \n")


if __name__ == "__main__":
    if "--avaliar" in sys.argv or "--eval" in sys.argv:
        modo_avaliacao()
    else:
        modo_interativo()
