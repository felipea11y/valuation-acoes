from __future__ import annotations

from collections.abc import Iterable


def calcular_nopat(
    ebit: float,
    aliquota_imposto: float,
) -> float:
    """Calcula NOPAT = EBIT × (1 - alíquota de imposto)."""
    if not 0 <= aliquota_imposto <= 1:
        raise ValueError("A alíquota de imposto deve estar entre 0 e 1.")

    return ebit * (1 - aliquota_imposto)


def calcular_fcff(
    nopat: float,
    depreciacao_amortizacao: float,
    capex: float,
    variacao_capital_giro: float,
) -> float:
    """Calcula FCFF = NOPAT + D&A - CAPEX - Δ capital de giro."""
    return (
        nopat
        + depreciacao_amortizacao
        - capex
        - variacao_capital_giro
    )


def calcular_wacc(
    valor_patrimonio: float,
    valor_divida: float,
    custo_patrimonio: float,
    custo_divida_pre_imposto: float,
    aliquota_imposto: float,
) -> float:
    """Calcula o WACC usando pesos de mercado de patrimônio e dívida."""
    if valor_patrimonio < 0 or valor_divida < 0:
        raise ValueError("Dívida e patrimônio não podem ser negativos.")

    if not 0 <= aliquota_imposto <= 1:
        raise ValueError("A alíquota de imposto deve estar entre 0 e 1.")

    total = valor_patrimonio + valor_divida
    if total <= 0:
        raise ValueError("A soma de dívida e patrimônio deve ser positiva.")

    peso_patrimonio = valor_patrimonio / total
    peso_divida = valor_divida / total

    return (
        peso_patrimonio * custo_patrimonio
        + peso_divida
        * custo_divida_pre_imposto
        * (1 - aliquota_imposto)
    )


def valor_presente_fluxo(
    fluxo: float,
    taxa_desconto: float,
    periodo: int,
) -> float:
    """Desconta um fluxo ao valor presente."""
    if taxa_desconto <= -1:
        raise ValueError("A taxa de desconto deve ser maior que -100%.")

    if periodo < 0:
        raise ValueError("O período não pode ser negativo.")

    return fluxo / ((1 + taxa_desconto) ** periodo)


def valor_presente_fcffs(
    fluxos: Iterable[float],
    taxa_desconto: float,
) -> float:
    """Soma o valor presente de FCFFs explícitos, iniciando no período 1."""
    return sum(
        valor_presente_fluxo(fluxo, taxa_desconto, periodo)
        for periodo, fluxo in enumerate(fluxos, start=1)
    )


def enterprise_para_equity(
    enterprise_value: float,
    caixa_e_equivalentes: float,
    divida_bruta: float,
    outros_ajustes: float = 0.0,
) -> float:
    """Converte Enterprise Value em Equity Value por ajustes financeiros explícitos."""
    return (
        enterprise_value
        + caixa_e_equivalentes
        - divida_bruta
        + outros_ajustes
    )
