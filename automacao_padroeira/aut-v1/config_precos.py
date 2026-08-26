#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração centralizada de preços para o cálculo de "Kg Equivalente".

Mantém os valores de conversão (R$/kg e preço unitário das refeições) em um
único lugar. Os preços base ficam AQUI (no código) e podem ser SOBRESCRITOS
por um arquivo opcional `config_precos.json` no mesmo diretório — assim ajustes
podem ser feitos sem editar este módulo.

Exemplo de config_precos.json:
{
  "REFEICAO_KG_PADRAO": 96.90,
  "REFEICAO_KG_SABADOS": 104.90,
  "REFEICAO_A_VONTADE": 63.90,
  "REFEICAO_TO_SAVE": 13.90,
  "OVERRIDE_KG_POR_DATA": {"2026-12-25": 96.90}
}

Regra de seleção do VALOR_KG_DIA (preço do quilo da refeição no dia):
  - Sábado            -> REFEICAO_KG_SABADOS
  - Segunda a Sexta   -> REFEICAO_KG_PADRAO
  - Feriados/promoções -> OVERRIDE_KG_POR_DATA (chave 'AAAA-MM-DD')
"""
import json
import os
from datetime import date
from typing import Dict, Any

# --- Preços base (R$) -------------------------------------------------------
REFEICAO_KG_GRILL = 144.90
REFEICAO_A_VONTADE = 63.90
REFEICAO_COM_SOBREMESA = 73.90
REFEICAO_KG_SABADOS = 104.90
REFEICAO_KG_PADRAO = 96.90      # dias úteis (segunda a sexta)
REFEICAO_TO_SAVE = 13.90

# --- Override do preço do KG por data específica ----------------------------
OVERRIDE_KG_POR_DATA: Dict[str, float] = {}


def _carregar_json() -> None:
    """Sobrescreve os preços base a partir de config_precos.json, se existir."""
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_precos.json")
    if not os.path.exists(caminho):
        return
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            cfg: Dict[str, Any] = json.load(f)
    except Exception:
        return
    for chave in (
        "REFEICAO_KG_GRILL", "REFEICAO_A_VONTADE", "REFEICAO_COM_SOBREMESA",
        "REFEICAO_KG_SABADOS", "REFEICAO_KG_PADRAO", "REFEICAO_TO_SAVE",
    ):
        if chave in cfg and cfg[chave] is not None:
            globals()[chave] = float(cfg[chave])
    if "OVERRIDE_KG_POR_DATA" in cfg and isinstance(cfg["OVERRIDE_KG_POR_DATA"], dict):
        OVERRIDE_KG_POR_DATA = {k: float(v) for k, v in cfg["OVERRIDE_KG_POR_DATA"].items()}
        globals()["OVERRIDE_KG_POR_DATA"] = OVERRIDE_KG_POR_DATA


_carregar_json()


def valor_kg_dia(data: date) -> float:
    """Retorna o preço do KG do dia (R$) conforme o dia da semana / override."""
    iso = data.isoformat()
    if iso in OVERRIDE_KG_POR_DATA:
        return float(OVERRIDE_KG_POR_DATA[iso])
    if data.weekday() == 5:          # sábado
        return float(REFEICAO_KG_SABADOS)
    return float(REFEICAO_KG_PADRAO)  # segunda a sexta (e domingo = padrão)


if __name__ == "__main__":
    for d in (date(2026, 7, 23), date(2026, 7, 25)):  # quinta e sábado
        print(f"{d} ({d.strftime('%A')}): VALOR_KG_DIA = R$ {valor_kg_dia(d):.2f}")
