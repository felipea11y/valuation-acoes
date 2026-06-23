import streamlit as st
import requests
import zipfile
import pandas as pd
import io

st.set_page_config(page_title="Valuation", layout="wide")
st.title("Analisador de Acoes")

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
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    
    with zf.open("dfp_cia_aberta_BPP_con_2025.csv") as f:
        bpp = pd.read_csv(f, sep=";", encoding="latin-1")
    with zf.open("dfp_cia_aberta_DRE_con_2025.csv") as f:
        dre = pd.read_csv(f, sep=";", encoding="latin-1")
    
    return {"bpp": bpp, "dre": dre}

def calcular_roic(cnpj, dfp):
    bpp = dfp["bpp"]
    dre = dfp["dre"]
    
    bpp = bpp[(bpp["CNPJ_CIA"] == cnpj) & (bpp["ORDEM_EXERC"] == "ULTIMO")]
    dre = dre[(dre["CNPJ_CIA"] == cnpj) & (dre["ORDEM_EXERC"] == "ULTIMO")]
