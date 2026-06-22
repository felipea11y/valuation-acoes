import streamlit as st
import requests
import zipfile
import pandas as pd
import io

st.set_page_config(page_title="Valuation de Acoes BR", layout="wide")

st.title("Analisador de Acoes Brasileiras")
st.markdown("Baseado em Aswath Damodaran - Dados CVM")
st.markdown("---")

def carregar_dados_cvm():
    with st.spinner("Carregando dados da CVM..."):
        url_fca = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_2026.zip"
        resposta_fca = requests.get(url_fca, timeout=30)
        arquivo_zip_fca = zipfile.ZipFile(io.BytesIO(resposta_fca.content))
        with arquivo_zip_fca.open("fca_cia_aberta_valor_mobiliario_2026.csv") as f:
            df_valores = pd.read_csv(f, sep=";", encoding="latin-1")
        
        url_dfp = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2025.zip"
        resposta_dfp = requests.get(url_dfp, timeout=30)
        arquivo_zip_dfp = zipfile.ZipFile(io.BytesIO(resposta_dfp.content))
    
    return df_valores, arquivo_zip_dfp

def buscar_cnpj_por_ticker(ticker, df_valores):
    resultado = df_valores[df_valores["Codigo_Negociacao"] == ticker]
    if len(resultado) == 0:
        return None, None
    return resultado["CNPJ_Companhia"].values[0], resultado["Nome_Empresarial"].values[0]

def buscar_dados_financeiros(cnpj, arquivo_zip_dfp):
    nome_arquivo_bpa = f"dfp_cia_aberta_BPA_con_2025.csv"
    with arquivo_zip_dfp.open(nome_arquivo_bpa) as f:
        df_bpa = pd.read_csv(f, sep=";", encoding="latin-1")
    df_bpa = df_bpa[(df_bpa["CNPJ_CIA"] == cnpj) & (df_bpa["ORDEM_EXERC"] == "ULTIMO")]
    
    nome_arquivo_bpp = f"dfp_cia_aberta_BPP_con_2025.csv"
    with arquivo_zip_dfp.open(nome_arquivo_bpp) as f:
        df_bpp = pd.read_csv(f, sep=";", encoding="latin-1")
    df_bpp = df_bpp[(df_bpp["CNPJ_CIA"] == cnpj) & (df_bpp["ORDEM_EXERC"] == "ULTIMO")]
    
    nome_arquivo_dre = f"dfp_cia_aberta_DRE_con_2025.csv"
    with arquivo_zip_dfp.open(nome_arquivo_dre) as f:
        df_dre = pd.read_csv(f, sep=";", encoding="latin-1")
    df_dre = df_dre[(df_dre["CNPJ_CIA"] == cnpj) & (df_dre["ORDEM_EXERC"] == "ULTIMO")]
    
    return {"bpa": df_bpa, "bpp": df_bpp, "dre": df_dre}

def calcular_roic(dados):
    df_bpp = dados["bpp"]
    df_dre = dados["dre"]
    
    if len(df_bpp) == 0 or len(df_dre) == 0:
        return None
    
    try:
        divida_curto = df_bpp[df_bpp["CD_CONTA"] == "2.01.04"]["VL_CONTA"].values[0]
        divida_longo = df_bpp[df_bpp["CD_CONTA"] == "2.02.01"]["VL_CONTA"].values[0]
        patrimonio = df_bpp[df_bpp["CD_CONTA"] == "2.03"]["VL_CONTA"].values[0]
        
        divida_total = divida_curto + divida_longo
        capital_investido = divida_total + patrimonio
        
        ebit = df_dre[df_dre["CD_CONTA"] == "3.05"]["VL_CONTA"].values[0]
        resultado_antes = df_dre[df_dre["CD_CONTA"] == "3.07"]["VL_CONTA"].values[0]
        impostos = df_dre[df_dre["CD_CONTA"] == "3.08"]["VL_CONTA"].values[0]
        
        aliquota = abs(impostos) / resultado_antes
        nopat = ebit * (1 - aliquota)
        roic = nopat / capital_investido
        
        return {"divida_total": divida_total, "capital_investido": capital_investido, "aliquota_efetiva": aliquota, "nopat": nopat, "roic": roic}
    except:
        return None

col1, col2 = st.columns([2, 1])

with col1:
    ticker_input = st.text_input("Digite o codigo da acao (ex: WEGE3, PETR4):", "WEGE3").upper()

with col2:
    analisar_button = st.button("Analisar", use_container_width=True)

st.markdown("---")

if analisar_button:
    with st.spinner("Carregando..."):
        df_valores, arquivo_zip_dfp = carregar_dados_cvm()
        cnpj, nome_empresa = buscar_cnpj_por_ticker(ticker_input, df_valores)
        
        if cnpj is None:
            st.error(f"Ticker {ticker_input} nao encontrado")
        else:
            dados = buscar_dados_financeiros(cnpj, arquivo_zip_dfp)
            resultado = calcular_roic(dados)
            
            if resultado is None:
                st.error("Erro ao calcular")
            else:
                st.success(f"Analise: {nome_empresa} ({ticker_input})")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ROIC", f"{resultado['roic']:.1%}")
                with col2:
                    st.metric("Capital Investido", f"R$ {resultado['capital_investido']/1_000_000:.2f} bi")
                with col3:
                    st.metric("NOPAT", f"R$ {resultado['nopat']:,.0f} mil")
                
                st.info(f"Divida Total: R$ {resultado['divida_total']:,.0f} mil")
                st.info(f"Aliquota Imposto: {resultado['aliquota_efetiva']:.1%}")

st.markdown("---")
st.markdown("CVM | Damodaran")
