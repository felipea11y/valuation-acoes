from __future__ import annotations

import io
import zipfile
from datetime import datetime

import pandas as pd
import requests


CVM_FCA_BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS"
CVM_DOC_BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC"

DEMONSTRACOES_SUPORTADAS = {
    "DRE",
    "BPA",
    "BPP",
    "DFC_MD",
    "DFC_MI",
    "DVA",
}


def _baixar_zip(url: str, timeout: int = 30) -> zipfile.ZipFile:
    resposta = requests.get(url, timeout=timeout)
    resposta.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(resposta.content))


def carregar_fca_valores_mobiliarios(ano: int, timeout: int = 30) -> pd.DataFrame:
    """Baixa e lê a tabela de valores mobiliários do FCA da CVM."""
    url = f"{CVM_FCA_BASE_URL}/fca_cia_aberta_{ano}.zip"
    nome_csv = f"fca_cia_aberta_valor_mobiliario_{ano}.csv"

    with _baixar_zip(url, timeout) as arquivo_zip:
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


def nome_arquivo_demonstracao(
    documento: str,
    demonstracao: str,
    ano: int,
    consolidado: bool = True,
) -> str:
    """Monta o nome de um CSV estruturado de DFP ou ITR."""
    documento = documento.upper()
    demonstracao = demonstracao.upper()

    if documento not in {"DFP", "ITR"}:
        raise ValueError("Documento deve ser DFP ou ITR.")

    if demonstracao not in DEMONSTRACOES_SUPORTADAS:
        raise ValueError(f"Demonstração não suportada: {demonstracao}")

    escopo = "con" if consolidado else "ind"
    prefixo = documento.lower()

    return f"{prefixo}_cia_aberta_{demonstracao}_{escopo}_{ano}.csv"


def carregar_demonstracao(
    documento: str,
    demonstracao: str,
    ano: int,
    consolidado: bool = True,
    timeout: int = 60,
) -> pd.DataFrame:
    """Baixa uma demonstração estruturada da CVM a partir do ZIP anual."""
    documento = documento.upper()
    prefixo = documento.lower()

    if documento not in {"DFP", "ITR"}:
        raise ValueError("Documento deve ser DFP ou ITR.")

    url = f"{CVM_DOC_BASE_URL}/{documento}/DADOS/{prefixo}_cia_aberta_{ano}.zip"
    nome_csv = nome_arquivo_demonstracao(
        documento,
        demonstracao,
        ano,
        consolidado,
    )

    with _baixar_zip(url, timeout) as arquivo_zip:
        with arquivo_zip.open(nome_csv) as arquivo_csv:
            return pd.read_csv(
                arquivo_csv,
                sep=";",
                encoding="latin-1",
                decimal=",",
            )


def filtrar_demonstracao_empresa(
    df: pd.DataFrame,
    cnpj: str,
    apenas_ultimo_exercicio: bool = True,
) -> pd.DataFrame:
    """Filtra uma demonstração pelo CNPJ e, opcionalmente, por ULTIMO exercício."""
    resultado = df[df["CNPJ_CIA"].astype(str) == str(cnpj)].copy()

    if apenas_ultimo_exercicio and "ORDEM_EXERC" in resultado.columns:
        resultado = resultado[resultado["ORDEM_EXERC"] == "ÚLTIMO"]

        if resultado.empty:
            resultado = df[
                (df["CNPJ_CIA"].astype(str) == str(cnpj))
                & (df["ORDEM_EXERC"] == "ULTIMO")
            ].copy()

    return resultado


def colunas_exibicao_demonstracao(df: pd.DataFrame) -> list[str]:
    """Retorna colunas relevantes presentes no DataFrame para exibição."""
    candidatas = [
        "DT_REFER",
        "CD_CONTA",
        "DS_CONTA",
        "VL_CONTA",
        "ST_CONTA_FIXA",
    ]
    return [coluna for coluna in candidatas if coluna in df.columns]
