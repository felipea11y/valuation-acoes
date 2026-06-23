import streamlit as st
import requests
import zipfile
import pandas as pd
import io

st.set_page_config(page_title="Valuation de Acoes", layout="wide")
st.title("Analisador de Acoes Brasileiras")

@st.cache_data
def carregar_cadastro():
    url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_2026.zip"
    resp = requests.get(url, timeout=30)
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    with zf.open("fca_cia_aberta_valor_mobiliario_2026.csv") as f:
        return pd.read_csv(f, sep=";", encoding="latin-1")

@st.cache_data
def carregar_dfp():
    url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2025.zip"
    resp = requests.get(url, timeout=30)
    return zipfile.ZipFile(io.BytesIO(resp.content))

try:
    df_cadastro = carregar_cadastro()
    arquivo_dfp = carregar_dfp()
    st.success(f"✓ {len(df_cadastro)} empresas carregadas")
    
    ticker = st.text_input("Ticker (ex: WEGE3, PETR4):", "WEGE3").upper()
    
    resultado = df_cadastro[df_cadastro["Codigo_Negociacao"] == ticker]
    
    if len(resultado) > 0:
        nome = resultado["Nome_Empresarial"].values[0]
        cnpj = resultado["CNPJ_Companhia"].values[0]
        st.info(f"✓ {nome}")
        st.write(f"CNPJ: {cnpj}")
    else:
        st.error("Nao encontrado")
        
except Exception as e:
    st.error(f"Erro: {str(e)}")
