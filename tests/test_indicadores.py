import pandas as pd

from src.indicadores import (
    calcular_cagr,
    calcular_indicadores_dre,
    extrair_valor_conta,
    montar_serie_historica_dre,
    resumo_crescimento_historico,
)


def test_extrair_valor_conta_por_codigo_exato():
    df = pd.DataFrame(
        {"CD_CONTA": ["3.01", "3.01.01", "3.11"], "VL_CONTA": [1000, 900, 100]}
    )
    assert extrair_valor_conta(df, "3.01") == 1000.0


def test_calcular_indicadores_dre():
    df = pd.DataFrame(
        {
            "CD_CONTA": ["3.01", "3.03", "3.05", "3.11"],
            "VL_CONTA": [1000, 400, 250, 150],
        }
    )
    resultado = calcular_indicadores_dre(df)

    assert resultado["receita"] == 1000.0
    assert resultado["resultado_bruto"] == 400.0
    assert resultado["resultado_operacional"] == 250.0
    assert resultado["lucro_liquido"] == 150.0
    assert resultado["margem_bruta"] == 0.4
    assert resultado["margem_operacional"] == 0.25
    assert resultado["margem_liquida"] == 0.15


def test_margens_ficam_indisponiveis_sem_receita():
    df = pd.DataFrame({"CD_CONTA": ["3.03", "3.11"], "VL_CONTA": [400, 150]})
    resultado = calcular_indicadores_dre(df)

    assert resultado["receita"] is None
    assert resultado["margem_bruta"] is None
    assert resultado["margem_liquida"] is None


def test_calcular_cagr():
    assert round(calcular_cagr(100, 121, 2), 6) == 0.1


def test_cagr_indisponivel_com_base_negativa():
    assert calcular_cagr(-100, 121, 2) is None


def test_montar_serie_historica_calcula_crescimento():
    anos = {
        2023: pd.DataFrame({"CD_CONTA": ["3.01", "3.11"], "VL_CONTA": [100, 10]}),
        2024: pd.DataFrame({"CD_CONTA": ["3.01", "3.11"], "VL_CONTA": [110, 12]}),
        2025: pd.DataFrame({"CD_CONTA": ["3.01", "3.11"], "VL_CONTA": [121, 15]}),
    }

    serie = montar_serie_historica_dre(anos)

    assert list(serie["ano"]) == [2023, 2024, 2025]
    assert round(serie.iloc[1]["crescimento_receita"], 6) == 0.1
    assert round(serie.iloc[2]["crescimento_receita"], 6) == 0.1


def test_resumo_crescimento_historico():
    serie = pd.DataFrame(
        {
            "ano": [2023, 2024, 2025],
            "receita": [100, 110, 121],
            "lucro_liquido": [10, 12, 14.4],
        }
    )

    resumo = resumo_crescimento_historico(serie)

    assert round(resumo["cagr_receita"], 6) == 0.1
    assert round(resumo["cagr_lucro"], 6) == 0.2
