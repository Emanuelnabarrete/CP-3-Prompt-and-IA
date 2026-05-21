

import json
import os
import tiktoken
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.chain import AssistantChain
from src.guardrails import GuardrailSystem
from src.schemas import ClassificacaoSchema


def count_tokens(texto: str) -> int:
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(texto))
    except Exception:
        return len(texto.split())


class Evaluator:
    def __init__(self):
        self.chain = AssistantChain()
        self.guardrails = GuardrailSystem()

    def _carregar_dataset(self, caminho: str) -> list:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)

    def avaliar_classificacao(self, dataset: list) -> dict:
        """Avalia se a etapa 1 classifica corretamente o tipo."""
        corretos = 0
        resultados = []

        for item in dataset:
            texto = item["texto"]
            esperado = item.get("tipo_esperado", "")

            is_safe, _ = self.guardrails.validar_input(texto)
            if not is_safe:
                resultados.append({
                    "texto": texto[:60],
                    "esperado": esperado,
                    "obtido": "BLOQUEADO",
                    "correto": False
                })
                continue

            try:
                classificacao = self.chain.etapa1_classificar(texto)
                obtido = classificacao.tipo
                correto = obtido == esperado
                if correto:
                    corretos += 1
                resultados.append({
                    "texto": texto[:60],
                    "esperado": esperado,
                    "obtido": obtido,
                    "correto": correto
                })
            except Exception as e:
                resultados.append({
                    "texto": texto[:60],
                    "esperado": esperado,
                    "obtido": f"ERRO: {e}",
                    "correto": False
                })

        total = len(dataset)
        acuracia = corretos / total if total > 0 else 0

        return {
            "acuracia": round(acuracia * 100, 1),
            "corretos": corretos,
            "total": total,
            "detalhes": resultados
        }

    def avaliar_json_valido(self, dataset: list) -> dict:
        """Avalia se o pipeline retorna JSON válido validado por Pydantic."""
        validos = 0
        resultados = []

        for item in dataset:
            texto = item["texto"]
            is_safe, _ = self.guardrails.validar_input(texto)
            if not is_safe:
                continue

            try:
                resultado = self.chain.processar(texto)
                # Se chegou aqui, Pydantic validou tudo
                validos += 1
                resultados.append({"texto": texto[:60], "json_valido": True})
            except Exception as e:
                resultados.append({"texto": texto[:60], "json_valido": False, "erro": str(e)})

        total = len([i for i in dataset])
        taxa = validos / total if total > 0 else 0

        return {
            "taxa_json_valido": round(taxa * 100, 1),
            "validos": validos,
            "total": total
        }

    def avaliar_bloqueio(self, attack_dataset: list) -> dict:
        """Avalia se os ataques são corretamente bloqueados."""
        bloqueados = 0
        resultados = []

        for item in attack_dataset:
            texto = item["texto"]
            tipo_ataque = item.get("tipo_ataque", "desconhecido")
            esperado = item.get("resultado_esperado", "BLOQUEADO")

            is_safe, motivo = self.guardrails.validar_input(texto)
            foi_bloqueado = not is_safe

            if foi_bloqueado and esperado == "BLOQUEADO":
                bloqueados += 1

            resultados.append({
                "texto": texto[:60],
                "tipo_ataque": tipo_ataque,
                "bloqueado": foi_bloqueado,
                "motivo": motivo,
                "correto": foi_bloqueado == (esperado == "BLOQUEADO")
            })

        total = len(attack_dataset)
        taxa = bloqueados / total if total > 0 else 0

        return {
            "taxa_bloqueio": round(taxa * 100, 1),
            "bloqueados": bloqueados,
            "total": total,
            "detalhes": resultados
        }

    def avaliar_falsos_positivos(self, dataset: list) -> dict:
        """Avalia se entradas legítimas são bloqueadas incorretamente."""
        falsos_positivos = 0
        resultados = []

        for item in dataset:
            texto = item["texto"]
            is_safe, motivo = self.guardrails.validar_input(texto)
            foi_bloqueado = not is_safe

            if foi_bloqueado:
                falsos_positivos += 1

            resultados.append({
                "texto": texto[:60],
                "bloqueado": foi_bloqueado,
                "motivo": motivo if foi_bloqueado else "ok"
            })

        total = len(dataset)
        taxa = falsos_positivos / total if total > 0 else 0

        return {
            "taxa_falso_positivo": round(taxa * 100, 1),
            "falsos_positivos": falsos_positivos,
            "total": total,
            "detalhes": resultados
        }

    def avaliar_consistencia(self, dataset: list, repeticoes: int = 3) -> dict:
        """Avalia se a mesma entrada retorna a mesma classificação (N vezes)."""
        resultados = []

        amostra = dataset[:5]  # Testa os 5 primeiros

        for item in amostra:
            texto = item["texto"]
            tipos = []

            for _ in range(repeticoes):
                is_safe, _ = self.guardrails.validar_input(texto)
                if not is_safe:
                    tipos.append("BLOQUEADO")
                    continue
                try:
                    c = self.chain.etapa1_classificar(texto)
                    tipos.append(c.tipo)
                except Exception:
                    tipos.append("ERRO")

            consistente = len(set(tipos)) == 1
            resultados.append({
                "texto": texto[:60],
                "classificacoes": tipos,
                "consistente": consistente
            })

        consistentes = sum(1 for r in resultados if r["consistente"])
        total = len(resultados)
        taxa = consistentes / total if total > 0 else 0

        return {
            "taxa_consistencia": round(taxa * 100, 1),
            "consistentes": consistentes,
            "total": total,
            "detalhes": resultados
        }

    def rodar_avaliacao_completa(self) -> dict:
        """Executa todas as métricas e gera relatório."""
        base = os.path.join(os.path.dirname(__file__), "..", "data")
        test_path = os.path.join(base, "test_dataset.json")
        attack_path = os.path.join(base, "attack_dataset.json")

        test_data = self._carregar_dataset(test_path)
        attack_data = self._carregar_dataset(attack_path)

        print("Avaliando classificação...")
        m1 = self.avaliar_classificacao(test_data)

        print("Avaliando JSON válido...")
        m2 = self.avaliar_json_valido(test_data)

        print("Avaliando bloqueio de ataques...")
        m3 = self.avaliar_bloqueio(attack_data)

        print("Avaliando falsos positivos...")
        m4 = self.avaliar_falsos_positivos(test_data)

        print("Avaliando consistência...")
        m5 = self.avaliar_consistencia(test_data)

        metricas = {
            "acuracia_classificacao": m1["acuracia"],
            "taxa_json_valido": m2["taxa_json_valido"],
            "taxa_bloqueio_ataques": m3["taxa_bloqueio"],
            "taxa_falso_positivo": m4["taxa_falso_positivo"],
            "taxa_consistencia": m5["taxa_consistencia"],
        }

        self._salvar_csv(metricas, m1, m3)
        self._gerar_graficos(metricas)

        return {
            "metricas_resumo": metricas,
            "detalhes": {
                "classificacao": m1,
                "bloqueio": m3,
                "falsos_positivos": m4,
                "consistencia": m5,
            }
        }

    def _salvar_csv(self, metricas, m1, m3):
        os.makedirs("output", exist_ok=True)

        # CSV de resultados gerais
        df = pd.DataFrame([metricas])
        df.to_csv("output/eval_results.csv", index=False)

        # CSV de detalhes de classificação
        if m1.get("detalhes"):
            pd.DataFrame(m1["detalhes"]).to_csv("output/classificacao_detalhes.csv", index=False)

        # CSV de ataques
        if m3.get("detalhes"):
            pd.DataFrame(m3["detalhes"]).to_csv("output/ataques_detalhes.csv", index=False)

    def _gerar_graficos(self, metricas):
        os.makedirs("output/graficos", exist_ok=True)

        labels = [
            "Acurácia\nClassificação",
            "JSON\nVálido",
            "Bloqueio\nAtaques",
            "Falso\nPositivo\n(inverso)",
            "Consistência"
        ]

        valores = [
            metricas["acuracia_classificacao"],
            metricas["taxa_json_valido"],
            metricas["taxa_bloqueio_ataques"],
            100 - metricas["taxa_falso_positivo"],  # invertido: menor é melhor
            metricas["taxa_consistencia"],
        ]

        cores = ["#4CAF50" if v >= 80 else "#FFC107" if v >= 60 else "#F44336" for v in valores]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(labels, valores, color=cores, width=0.5, edgecolor="white")
        ax.set_ylim(0, 110)
        ax.set_ylabel("Taxa (%)", fontsize=12)
        ax.set_title("TechStore Smart Assistant — Métricas de Avaliação", fontsize=14, fontweight="bold")
        ax.axhline(80, color="gray", linestyle="--", linewidth=0.8, label="Meta 80%")
        ax.legend()

        for bar, val in zip(bars, valores):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{val:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

        plt.tight_layout()
        plt.savefig("output/graficos/metricas_avaliacao.png", dpi=150)
        plt.close()

        # Gráfico de radar (spider)
        import numpy as np
        categorias = ["Acurácia", "JSON Válido", "Anti-Ataque", "Sem FP", "Consistência"]
        N = len(categorias)
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += angles[:1]
        vals = valores + [valores[0]]

        fig2, ax2 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax2.plot(angles, vals, "o-", linewidth=2, color="#2196F3")
        ax2.fill(angles, vals, alpha=0.25, color="#2196F3")
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(categorias, fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.set_title("Radar de Performance", fontsize=13, fontweight="bold", pad=20)
        plt.tight_layout()
        plt.savefig("output/graficos/radar_performance.png", dpi=150)
        plt.close()

        print("✅ Gráficos salvos em output/graficos/")
