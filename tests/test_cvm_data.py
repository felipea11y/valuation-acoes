import pandas as pd
import pytest

from src.cvm_data import (
    anos_candidatos,
    buscar_empresa,
    colunas_exibicao_demonstracao,
    filtrar_demonstracao_empresa,
    nome_arquivo_demonstracao,
)


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


def test_nome_arquivo_dfp_dre_consolidada():
    assert (
        nome_arquivo_demonstracao("DFP", "DRE", 2025)
        == "dfp_cia_aberta_DRE_con_2025.csv"
    )


def test_nome_arquivo_itr_bpp_individual():
    assert (
        nome_arquivo_demonstracao("itr", "bpp", 2026, consolidado=False)
        == "itr_cia_aberta_BPP_ind_2026.csv"
    )


def test_documento_invalido():
    with pytest.raises(ValueError):
        nome_arquivo_demonstracao("FCA", "DRE", 2025)


def test_filtrar_demonstracao_por_cnpj_e_ultimo_exercicio():
    df = pd.DataFrame(
        {
            "CNPJ_CIA": ["1", "1", "2"],
            "ORDEM_EXERC": ["ÚLTIMO", "PENÚLTIMO", "ÚLTIMO"],
            "CD_CONTA": ["3.01", "3.01", "3.01"],
        }
    )

    resultado = filtrar_demonstracao_empresa(df, "1")

    assert len(resultado) == 1
    assert resultado.iloc[0]["ORDEM_EXERC"] == "ÚLTIMO"


def test_colunas_exibicao_retorna_apenas_existentes():
    df = pd.DataFrame(
        {
            "CD_CONTA": ["3.01"],
            "DS_CONTA": ["Receita"],
            "VL_CONTA": [100],
            "OUTRA": ["x"],
        }
    )

    assert colunas_exibicao_demonstracao(df) == [
        "CD_CONTA",
        "DS_CONTA",
        "VL_CONTA",
    ]
