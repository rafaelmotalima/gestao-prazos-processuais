"""
Prova: lógica do painel (dashboard) de prazos.

Fica separada da view para ser fácil de testar: recebe a data de "hoje"
como parâmetro e devolve apenas dados simples (dicionários e listas).
"""
from collections import OrderedDict

from .models import Prazo

# Ordem em que os níveis aparecem no painel (do mais grave para o mais tranquilo)
NIVEIS = ["VENCIDO", "VERMELHO", "AMARELO", "VERDE", "CUMPRIDO"]

ROTULOS = {
    "VENCIDO": "Vencido",
    "VERMELHO": "Urgente (até 3 dias)",
    "AMARELO": "Atenção (4 a 7 dias)",
    "VERDE": "No prazo (mais de 7 dias)",
    "CUMPRIDO": "Cumprido",
}

CORES = {
    "VENCIDO": "#7f1d1d",
    "VERMELHO": "#c0392b",
    "AMARELO": "#d4a017",
    "VERDE": "#2e8b57",
    "CUMPRIDO": "#6b7280",
}


def montar_painel(hoje=None):
    prazos = list(Prazo.objects.select_related("processo__cliente"))

    contagem = OrderedDict((n, 0) for n in NIVEIS)
    por_cliente = {}
    pendentes = []

    for p in prazos:
        nivel = p.nivel_alerta(hoje)
        contagem[nivel] += 1

        cliente = p.processo.cliente.nome if p.processo.cliente else "Sem cliente"
        linha = por_cliente.setdefault(
            cliente, {"cliente": cliente, "pendentes": 0, "criticos": 0, "proximo": None}
        )
        if nivel != "CUMPRIDO":
            linha["pendentes"] += 1
            if nivel in ("VENCIDO", "VERMELHO"):
                linha["criticos"] += 1
            if linha["proximo"] is None or p.data_vencimento < linha["proximo"]:
                linha["proximo"] = p.data_vencimento
            pendentes.append(
                {
                    "prazo": p,
                    "cliente": cliente,
                    "dias": p.dias_restantes(hoje),
                    "nivel": nivel,
                    "cor": CORES[nivel],
                    "rotulo": ROTULOS[nivel].split(" (")[0],
                }
            )

    pendentes.sort(key=lambda x: x["prazo"].data_vencimento)

    total_pendentes = sum(v for k, v in contagem.items() if k != "CUMPRIDO")
    maior = max(contagem.values()) if contagem else 0
    grafico = [
        {
            "nivel": n,
            "rotulo": ROTULOS[n],
            "cor": CORES[n],
            "total": contagem[n],
            "largura": round(100 * contagem[n] / maior) if maior else 0,
        }
        for n in NIVEIS
    ]

    clientes = sorted(
        (c for c in por_cliente.values() if c["pendentes"] > 0),
        key=lambda c: (-c["criticos"], -c["pendentes"], c["cliente"]),
    )

    return {
        "total": len(prazos),
        "total_pendentes": total_pendentes,
        "contagem": contagem,
        "grafico": grafico,
        "clientes": clientes,
        "proximos": pendentes[:10],
    }
