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


def calcular_cagr(
    valor_inicial: float | None,
    valor_final: float | None,
    periodos: int,
) -> float | None:
    """Calcula CAGR quando valores e número de períodos permitem o cálculo."""
    if (
        valor_inicial is None
        or valor_final is None
        or valor_inicial <= 0
        or valor_final <= 0
        or periodos <= 0
    ):
        return None

    return (valor_final / valor_inicial) ** (1 / periodos) - 1


def montar_serie_historica_dre(
    demonstracoes_por_ano: dict[int, pd.DataFrame],
) -> pd.DataFrame:
    """Consolida indicadores anuais da DRE e calcula variações ano a ano."""
    linhas: list[dict[str, float | int | None]] = []

    for ano in sorted(demonstracoes_por_ano):
        indicadores = calcular_indicadores_dre(demonstracoes_por_ano[ano])
        linhas.append({"ano": ano, **indicadores})

    serie = pd.DataFrame(linhas)
    if serie.empty:
        return serie

    serie["crescimento_receita"] = serie["receita"].pct_change(fill_method=None)
    serie["crescimento_lucro"] = serie["lucro_liquido"].pct_change(fill_method=None)
    return serie


def resumo_crescimento_historico(serie: pd.DataFrame) -> dict[str, float | None]:
    """Calcula CAGR da receita e do lucro entre o primeiro e o último ano."""
    if len(serie) < 2:
        return {"cagr_receita": None, "cagr_lucro": None}

    ordenada = serie.sort_values("ano").reset_index(drop=True)
    periodos = int(ordenada.iloc[-1]["ano"] - ordenada.iloc[0]["ano"])

    return {
        "cagr_receita": calcular_cagr(
            ordenada.iloc[0]["receita"],
            ordenada.iloc[-1]["receita"],
            periodos,
        ),
        "cagr_lucro": calcular_cagr(
            ordenada.iloc[0]["lucro_liquido"],
            ordenada.iloc[-1]["lucro_liquido"],
            periodos,
        ),
    }
