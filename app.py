import io
import zipfile
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="Valuation de Ações",
    page_icon="📊",
    layout="wide",
)

st.title("Analisador de Ações Brasileiras")
st.caption(
    "Protótipo acadêmico para consulta de companhias abertas e evolução "
    "futura para análise fundamentalista e valuation."
)

CVM_FCA_BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS"


@st.cache_data(ttl=86_400)
def carregar_cadastro(ano: int) -> pd.DataFrame:
    """Carrega a tabela de valores mobiliários do FCA publicada pela CVM."""
    url = f"{CVM_FCA_BASE_URL}/fca_cia_aberta_{ano}.zip"
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resposta.content)) as arquivo_zip:
        nome_csv = f"fca_cia_aberta_valor_mobiliario_{ano}.csv"
        with arquivo_zip.open(nome_csv) as arquivo_csv:
            return pd.read_csv(
                arquivo_csv,
                sep=";",
                encoding="latin-1",
            )


def carregar_cadastro_mais_recente() -> tuple[pd.DataFrame, int]:
    """Tenta o ano atual e, se necessário, o ano anterior."""
    ano_atual = datetime.now().year
    ultimo_erro: Exception | None = None

    for ano in (ano_atual, ano_atual - 1):
        try:
            return carregar_cadastro(ano), ano
        except (requests.RequestException, zipfile.BadZipFile, KeyError, ValueError) as erro:
            ultimo_erro = erro

    if ultimo_erro is not None:
        raise ultimo_erro

    raise RuntimeError("Não foi possível determinar uma base FCA disponível.")


def buscar_empresa(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Retorna os registros do FCA correspondentes ao ticker informado."""
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


try:
    with st.spinner("Carregando cadastro da CVM..."):
        df_cadastro, ano_base = carregar_cadastro_mais_recente()

    st.success(
        f"Cadastro CVM {ano_base} carregado: "
        f"{len(df_cadastro):,} registros."
    )

    ticker = st.text_input(
        "Ticker (ex.: WEGE3, PETR4)",
        "WEGE3",
    )

    resultado = buscar_empresa(df_cadastro, ticker)

    if ticker.strip():
        if not resultado.empty:
            empresa = resultado.iloc[0]

            st.subheader(str(empresa["Nome_Empresarial"]))
            st.write(f"**Ticker:** {ticker.strip().upper()}")
            st.write(f"**CNPJ:** {empresa['CNPJ_Companhia']}")

            if len(resultado) > 1:
                st.caption(
                    f"O ticker possui {len(resultado)} registros na tabela consultada; "
                    "o primeiro foi usado para esta visualização."
                )

            st.info(
                "Etapa atual: identificação cadastral. Indicadores financeiros "
                "e valuation ainda não estão implementados."
            )
        else:
            st.warning("Ticker não encontrado no cadastro consultado da CVM.")

    st.markdown(
        "Fonte: [Portal de Dados Abertos da CVM]"
        "(https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca)"
    )

except (requests.RequestException, zipfile.BadZipFile, KeyError, ValueError) as erro:
    st.error("Não foi possível carregar ou interpretar os dados da CVM.")
    st.caption(f"Detalhe técnico: {erro}")
