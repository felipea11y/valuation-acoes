import streamlit as st
import requests
import zipfile
import pandas as pd
import io

st.title("Analisador de Acoes")

try:
    st.write("Carregando dados...")
    
    url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_2026.zip"
    resp = requests.get(url, timeout=30)
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    
    with zf.open("fca_cia_aberta_valor_mobiliario_2026.csv") as f:
        df = pd.read_csv(f, sep=";", encoding="latin-1")
    
    st.write(f"OK - {len(df)} empresas carregadas")
    
    ticker = st.text_input("Ticker:", "WEGE3").upper()
    
    resultado = df[df["Codigo_Negociacao"] == ticker]
    
    if len(resultado) > 0:
        nome = resultado["Nome_Empresarial"].values[0]
        cnpj = resultado["CNPJ_Companhia"].values[0]
        st.success(f"Encontrado: {nome}")
        st.write(f"CNPJ: {cnpj}")
    else:
        st.error("Nao encontrado")
        
except Exception as e:
    st.error(f"Erro: {str(e)}")
