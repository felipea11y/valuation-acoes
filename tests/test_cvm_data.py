import pandas as pd

from src.cvm_data import anos_candidatos, buscar_empresa


def test_anos_candidatos_inclui_ano_anterior():
    assert anos_candidatos(2026) == (2026, 2025)


def test_buscar_empresa_normaliza_ticker():
    df = pd.DataFrame(
        {
            "Codigo_Negociacao": ["WEGE3", " PETR4 ", None],
            "Nome_Empresarial": ["WEG", "Petrobras", "Sem ticker"],
        }
    )

    resultado = buscar_empresa(df, " petr4 ")

    assert len(resultado) == 1
    assert resultado.iloc[0]["Nome_Empresarial"] == "Petrobras"


def test_buscar_empresa_com_ticker_vazio_retorna_vazio():
    df = pd.DataFrame({"Codigo_Negociacao": ["WEGE3"]})

    resultado = buscar_empresa(df, "   ")

    assert resultado.empty
