import pytest

from src.valuation import (
    calcular_fcff,
    calcular_nopat,
    calcular_wacc,
    enterprise_para_equity,
    valor_presente_fcffs,
    valor_presente_fluxo,
)


def test_calcular_nopat():
    assert calcular_nopat(100, 0.34) == pytest.approx(66)


def test_nopat_rejeita_aliquota_invalida():
    with pytest.raises(ValueError):
        calcular_nopat(100, 1.1)


def test_calcular_fcff():
    assert calcular_fcff(
        nopat=100,
        depreciacao_amortizacao=20,
        capex=30,
        variacao_capital_giro=10,
    ) == pytest.approx(80)


def test_calcular_wacc():
    wacc = calcular_wacc(
        valor_patrimonio=600,
        valor_divida=400,
        custo_patrimonio=0.12,
        custo_divida_pre_imposto=0.08,
        aliquota_imposto=0.25,
    )

    assert wacc == pytest.approx(0.096)


def test_wacc_rejeita_capital_total_zero():
    with pytest.raises(ValueError):
        calcular_wacc(0, 0, 0.12, 0.08, 0.25)


def test_valor_presente_fluxo():
    assert valor_presente_fluxo(110, 0.10, 1) == pytest.approx(100)


def test_valor_presente_fcffs():
    resultado = valor_presente_fcffs([110, 121], 0.10)

    assert resultado == pytest.approx(200)


def test_enterprise_para_equity():
    assert enterprise_para_equity(
        enterprise_value=1000,
        caixa_e_equivalentes=150,
        divida_bruta=300,
    ) == pytest.approx(850)
