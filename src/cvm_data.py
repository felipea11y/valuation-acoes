from __future__ import annotations

import io
import zipfile
from datetime import datetime

import pandas as pd
import requests


CVM_FCA_BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS"


def carregar_fca_valores_mobiliarios(ano: int, timeout: int = 30) -> pd.DataFrame:
    """Baixa e lê a tabela de valores mobiliários do FCA da CVM."""
    url = f"{CVM_FCA_BASE_URL}/fca_cia_aberta_{ano}.zip"
    resposta = requests.get(url, timeout=timeout)
    resposta.raise_for_status()

    nome_csv = f"fca_cia_aberta_valor_mobiliario_{ano}.csv"

    with zipfile.ZipFile(io.BytesIO(resposta.content)) as arquivo_zip:
        with arquivo_zip.open(nome_csv) as arquivo_csv:
            return pd.read_csv(arquivo_csv, sep=";", encoding="latin-1")


def anos_candidatos(ano_referencia: int | None = None) -> tuple[int, int]:
    """Retorna o ano de referência e o anterior para fallback."""
    ano = ano_referencia or datetime.now().year
    return ano, ano - 1


def carregar_fca_mais_recente(
    ano_referencia: int | None = None,
) -> tuple[pd.DataFrame, int]:
    """Tenta carregar o FCA do ano de referência e, depois, o ano anterior."""
    ultimo_erro: Exception | None = None

    for ano in anos_candidatos(ano_referencia):
        try:
            return carregar_fca_valores_mobiliarios(ano), ano
        except (
            requests.RequestException,
            zipfile.BadZipFile,
            KeyError,
            ValueError,
        ) as erro:
            ultimo_erro = erro

    if ultimo_erro is not None:
        raise ultimo_erro

    raise RuntimeError("Não foi possível determinar uma base FCA disponível.")


def buscar_empresa(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Filtra registros do FCA pelo código de negociação."""
    ticker_normalizado = ticker.strip().upper()

    if not ticker_normalizado:
        return df.iloc[0:0]

    codigos = (
        df["Codigo_Negociacao"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df[codigos == ticker_normalizado]
