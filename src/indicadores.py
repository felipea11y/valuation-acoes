from __future__ import annotations

import math

import pandas as pd


CONTAS_DRE = {
    "receita": "3.01",
    "resultado_bruto": "3.03",
    "resultado_operacional": "3.05",
    "lucro_liquido": "3.11",
}


def extrair_valor_conta(df: pd.DataFrame, codigo_conta: str) -> float | None:
    """Extrai o valor da linha padronizada correspondente ao código exato."""
    if "CD_CONTA" not in df.columns or "VL_CONTA" not in df.columns:
        return None

    linhas = df[df["CD_CONTA"].astype(str).str.strip() == codigo_conta]

    if linhas.empty:
        return None

    valor = pd.to_numeric(linhas.iloc[0]["VL_CONTA"], errors="coerce")

    if pd.isna(valor):
        return None

    return float(valor)


def _margem(resultado: float | None, receita: float | None) -> float | None:
    if resultado is None or receita in (None, 0):
        return None

    margem = resultado / receita

    if not math.isfinite(margem):
        return None

    return margem


def calcular_indicadores_dre(df: pd.DataFrame) -> dict[str, float | None]:
    """Calcula indicadores descritivos a partir das linhas padronizadas da DRE."""
    receita = extrair_valor_conta(df, CONTAS_DRE["receita"])
    bruto = extrair_valor_conta(df, CONTAS_DRE["resultado_bruto"])
    operacional = extrair_valor_conta(df, CONTAS_DRE["resultado_operacional"])
    lucro = extrair_valor_conta(df, CONTAS_DRE["lucro_liquido"])

    return {
        "receita": receita,
        "resultado_bruto": bruto,
        "resultado_operacional": operacional,
        "lucro_liquido": lucro,
        "margem_bruta": _margem(bruto, receita),
        "margem_operacional": _margem(operacional, receita),
        "margem_liquida": _margem(lucro, receita),
    }
