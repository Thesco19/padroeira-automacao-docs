#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
regen_faturamento.py — regenera historico_faturamento/faturamento_diario.json
a partir do fechamento_caixa_2026-08-27.txt INTEGRO (o JSON original foi
removido em 28/08 ~00:09, mas o .txt de origem permanece).

NAO importa bot_reconciliation.py de proposito: a importacao dele cria um
FileHandler(LOGFILE, mode="w") que truncaria o reconciliation.log (prova
forense do /fechar). Usamos so o parser do cortex + reimplementacao FIEL das
funcoes _fmt_num e _salvar_historico_faturamento do bot, para gerar um JSON
identico ao produzido pelo /fechar. Dev em testes/; artefato vai para
historico_faturamento/ (lido pelo /finalizar). Nao toca no Box.
"""
import importlib.util
import json
import os
import sys
from datetime import datetime

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # aut-v1
sys.path.insert(0, WORK)  # cortex importa calendario_padroeira (local)
HIST_DIR = os.path.join(WORK, "historico_faturamento")
HIST_FILE = os.path.join(HIST_DIR, "faturamento_diario.json")


def _carregar(modulo, caminho):
    spec = importlib.util.spec_from_file_location(modulo, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[modulo] = m
    spec.loader.exec_module(m)
    return m


# Parser do Córtex (reusado exatamente como no /fechar).
cortex = _carregar("cortex_padroeira_async", os.path.join(WORK, "cortex_padroeira_async.py"))


def _fmt_num(s):
    """Copia fiel de bot_reconciliation._fmt_num (pos-correcao 28/08)."""
    if s is None:
        return 0.0
    try:
        return float(str(s).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def _salvar_historico_faturamento(registro):
    """Copia fiel de bot_reconciliation._salvar_historico_faturamento."""
    if registro.get("erro"):
        return False
    try:
        historico = {}
        if os.path.exists(HIST_FILE):
            with open(HIST_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
        d = registro.get("dados") or {}
        historico[registro["data"]] = {
            "aamm": registro["aamm"],
            "total": _fmt_num(d.get("total")),
            "dinheiro": _fmt_num(d.get("dinheiro")),
            "credito": _fmt_num(d.get("credito")),
            "debito": _fmt_num(d.get("debito")),
            "clientes": d.get("clientes"),
            "kg_eq_ref": d.get("kg_eq_ref"),
            "kg_eq_sob": d.get("kg_eq_sob"),
            "entrou_saurus": registro.get("entrou_saurus", False),
            "salvo_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(HIST_FILE, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# --- Regenera o fechamento de 27/08/2026 (perdeu o JSON, mas o .txt existe) ---
DATA_ISO = "2026-08-27"
DATA_BR = "27/08/2026"
AAMM = "2608"

dados = cortex.CortexPadroeiraAsync(base_dir=WORK).extrair_dados_saurus_por_data(DATA_ISO)
if not dados:
    print(f"[ERRO] Parser nao leu fechamento_caixa_{DATA_ISO}.txt — abortando.")
    sys.exit(1)

registro = {
    "erro": None,
    "data": DATA_BR,
    "aamm": AAMM,
    "entrou_saurus": False,
    "do_cache": True,  # origem: ./fechamentos (nao reentrou no Saurus)
    "dados": dados,
}

salvou = _salvar_historico_faturamento(registro)
print(f"[{'OK' if salvou else 'FALHOU'}] historico regenerado para {DATA_BR} -> {HIST_FILE}")
if salvou:
    with open(HIST_FILE, "r", encoding="utf-8") as f:
        h = json.load(f)
    reg = h.get(DATA_BR, {})
    print("   total:", reg.get("total"), "| dinheiro:", reg.get("dinheiro"),
          "| credito:", reg.get("credito"), "| debito:", reg.get("debito"),
          "| clientes:", reg.get("clientes"),
          "| kg_eq_ref:", reg.get("kg_eq_ref"), "| kg_eq_sob:", reg.get("kg_eq_sob"))
