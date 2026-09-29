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


HORIZONTE_PADRAO_ANOS = 5


def validar_horizonte(horizonte_anos: int) -> int:
    """Valida e retorna o horizonte explícito do DCF."""
    if not isinstance(horizonte_anos, int):
        raise TypeError("O horizonte deve ser informado em anos inteiros.")

    if horizonte_anos <= 0:
        raise ValueError("O horizonte deve ser maior que zero.")

    return horizonte_anos


def validar_fluxos_horizonte(
    fluxos: Iterable[float],
    horizonte_anos: int = HORIZONTE_PADRAO_ANOS,
) -> list[float]:
    """Valida se há exatamente um FCFF explícito por ano do horizonte."""
    horizonte = validar_horizonte(horizonte_anos)
    lista_fluxos = list(fluxos)

    if len(lista_fluxos) != horizonte:
        raise ValueError(
            f"Esperados {horizonte} FCFFs para o horizonte explícito, "
            f"mas foram recebidos {len(lista_fluxos)}."
        )

    return lista_fluxos


def cronograma_fcff_explicito(
    fluxos: Iterable[float],
    taxa_desconto: float,
    horizonte_anos: int = HORIZONTE_PADRAO_ANOS,
) -> list[dict[str, float | int]]:
    """Monta o cronograma de FCFFs explícitos e seus valores presentes."""
    lista_fluxos = validar_fluxos_horizonte(fluxos, horizonte_anos)

    return [
        {
            "ano": periodo,
            "fcff": fluxo,
            "fator_desconto": 1 / ((1 + taxa_desconto) ** periodo),
            "valor_presente": valor_presente_fluxo(
                fluxo,
                taxa_desconto,
                periodo,
            ),
        }
        for periodo, fluxo in enumerate(lista_fluxos, start=1)
    ]


def valor_presente_periodo_explicito(
    fluxos: Iterable[float],
    taxa_desconto: float,
    horizonte_anos: int = HORIZONTE_PADRAO_ANOS,
) -> float:
    """Calcula o valor presente apenas do período explícito do DCF."""
    cronograma = cronograma_fcff_explicito(
        fluxos,
        taxa_desconto,
        horizonte_anos,
    )

    return sum(item["valor_presente"] for item in cronograma)


def validar_taxas_crescimento(
    taxas: Iterable[float],
    horizonte_anos: int = HORIZONTE_PADRAO_ANOS,
) -> list[float]:
    """Valida uma taxa de crescimento explícita para cada ano projetado."""
    horizonte = validar_horizonte(horizonte_anos)
    lista_taxas = list(taxas)

    if len(lista_taxas) != horizonte:
        raise ValueError(
            f"Esperadas {horizonte} taxas de crescimento, "
            f"mas foram recebidas {len(lista_taxas)}."
        )

    for taxa in lista_taxas:
        if taxa <= -1:
            raise ValueError(
                "Cada taxa de crescimento deve ser maior que -100%."
            )

    return lista_taxas


def projetar_receitas(
    receita_base: float,
    taxas_crescimento: Iterable[float],
    horizonte_anos: int = HORIZONTE_PADRAO_ANOS,
) -> list[dict[str, float | int]]:
    """Projeta receita ano a ano a partir de premissas explícitas de crescimento."""
    if receita_base < 0:
        raise ValueError("A receita base não pode ser negativa.")

    taxas = validar_taxas_crescimento(
        taxas_crescimento,
        horizonte_anos,
    )

    receita = float(receita_base)
    projecoes: list[dict[str, float | int]] = []

    for ano, taxa in enumerate(taxas, start=1):
        receita *= 1 + taxa
        projecoes.append(
            {
                "ano": ano,
                "taxa_crescimento": taxa,
                "receita": receita,
            }
        )

    return projecoes
