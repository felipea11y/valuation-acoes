import pandas as pd

from src.indicadores import calcular_indicadores_dre, extrair_valor_conta


def test_extrair_valor_conta_por_codigo_exato():
    df = pd.DataFrame(
        {
            "CD_CONTA": ["3.01", "3.01.01", "3.11"],
            "VL_CONTA": [1000, 900, 100],
        }
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
    df = pd.DataFrame(
        {
            "CD_CONTA": ["3.03", "3.11"],
            "VL_CONTA": [400, 150],
        }
    )

    resultado = calcular_indicadores_dre(df)

    assert resultado["receita"] is None
    assert resultado["margem_bruta"] is None
    assert resultado["margem_liquida"] is None
