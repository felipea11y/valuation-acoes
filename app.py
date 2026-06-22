import streamlit as st
import requests
import zipfile
import pandas as pd
import io
import yfinance as yf

st.set_page_config(page_title="Valuation de Acoes BR", layout="wide")

st.title("Analisador de Acoes Brasileiras")
st.markdown("Baseado em metodologia de Aswath Damodaran")
st.markdown("---")

def carregar_dados_cvm():
    with st.spinner("Carregando dados da CVM (primeira vez)..."):
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

def buscar_dados_financeiros(cnpj, arquivo_zip_dfp, ano_dfp=2025, ordem_exerc="ULTIMO"):
    nome_arquivo_bpa = f"dfp_cia_aberta_BPA_con_{ano_dfp}.csv"
    with arquivo_zip_dfp.open(nome_arquivo_bpa) as f:
        df_bpa = pd.read_csv(f, sep=";", encoding="latin-1")
    df_bpa = df_bpa[(df_bpa["CNPJ_CIA"] == cnpj) & (df_bpa["ORDEM_EXERC"] == ordem_exerc)]
    
    nome_arquivo_bpp = f"dfp_cia_aberta_BPP_con_{ano_dfp}.csv"
    with arquivo_zip_dfp.open(nome_arquivo_bpp) as f:
        df_bpp = pd.read_csv(f, sep=";", encoding="latin-1")
    df_bpp = df_bpp[(df_bpp["CNPJ_CIA"] == cnpj) & (df_bpp["ORDEM_EXERC"] == ordem_exerc)]
    
    nome_arquivo_dre = f"dfp_cia_aberta_DRE_con_{ano_dfp}.csv"
    with arquivo_zip_dfp.open(nome_arquivo_dre) as f:
        df_dre = pd.read_csv(f, sep=";", encoding="latin-1")
    df_dre = df_dre[(df_dre["CNPJ_CIA"] == cnpj) & (df_dre["ORDEM_EXERC"] == ordem_exerc)]
    
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
        
        return {
            "divida_total": divida_total,
            "patrimonio_liquido": patrimonio,
            "capital_investido": capital_investido,
            "aliquota_efetiva": aliquota,
            "nopat": nopat,
            "roic": roic
        }
    except:
        return None

def buscar_beta_acao(ticker):
    try:
        acao = yf.Ticker(ticker + ".SA")
        beta = acao.info.get("beta")
        if beta is None or beta < 0 or beta > 2.0:
            return 1.1
        return beta
    except:
        return 1.1

def calcular_market_cap(ticker):
    try:
        acao = yf.Ticker(ticker + ".SA")
        market_cap = acao.info.get("marketCap")
        if market_cap is None:
            return None
        return market_cap / 1000
    except:
        return None

def calcular_capm(beta, rf=0.10, premio_risco=0.075):
    return rf + beta * premio_risco

def calcular_wacc(market_cap, divida_total, re, rd, aliquota):
    divida_bi = divida_total / 1_000_000
    valor_total = market_cap + divida_bi
    peso_patrimonio = market_cap / valor_total
    peso_divida = divida_bi / valor_total
    wacc = (peso_patrimonio * re) + (peso_divida * rd * (1 - aliquota))
    
    return {
        "market_cap": market_cap,
        "divida": divida_bi,
        "valor_total": valor_total,
        "peso_patrimonio": peso_patrimonio,
        "peso_divida": peso_divida,
        "re": re,
        "rd": rd,
        "wacc": wacc
    }

col1, col2 = st.columns([2, 1])

with col1:
    ticker_input = st.text_input("Digite o codigo da acao (ex: WEGE3, PETR4, VALE3):", "WEGE3").upper()

with col2:
    analisar_button = st.button("Analisar", use_container_width=True)

st.markdown("---")

if analisar_button:
    with st.spinner("Carregando dados..."):
        df_valores, arquivo_zip_dfp = carregar_dados_cvm()
        cnpj, nome_empresa = buscar_cnpj_por_ticker(ticker_input, df_valores)
        
        if cnpj is None:
            st.error(f"Ticker {ticker_input} nao encontrado no cadastro da CVM")
        else:
            dados = buscar_dados_financeiros(cnpj, arquivo_zip_dfp)
            resultado_roic = calcular_roic(dados)
            
            if resultado_roic is None:
                st.error("Erro ao calcular ROIC")
            else:
                market_cap = calcular_market_cap(ticker_input)
                beta = buscar_beta_acao(ticker_input)
                re = calcular_capm(beta)
                rd = 0.12
                wacc_resultado = calcular_wacc(market_cap, resultado_roic["divida_total"], re, rd, resultado_roic["aliquota_efetiva"])
                
                st.success(f"Analise de {nome_empresa} ({ticker_input})")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("ROIC", f"{resultado_roic['roic']:.1%}")
                
                with col2:
                    st.metric("WACC", f"{wacc_resultado['wacc']:.2%}")
                
                with col3:
                    spread = resultado_roic['roic'] - wacc_resultado['wacc']
                    st.metric("Spread (ROIC-WACC)", f"{spread:.2%}")
                
                st.markdown("### Detalhes")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Estrutura de Capital:**")
                    st.write(f"Market Cap: R$ {wacc_resultado['market_cap']:.2f} bi")
                    st.write(f"Divida: R$ {wacc_resultado['divida']:.2f} bi")
                    st.write(f"Total: R$ {wacc_resultado['valor_total']:.2f} bi")
                
                with col2:
                    st.write("**Custos:**")
                    st.write(f"Beta: {beta:.2f}")
                    st.write(f"Re: {wacc_resultado['re']:.2%}")
                    st.write(f"Rd: {wacc_resultado['rd']:.2%}")
                
                st.markdown("### Conclusao")
                if resultado_roic['roic'] > wacc_resultado['wacc']:
                    st.success(f"ROIC > WACC: Cria valor")
                else:
                    st.error(f"ROIC < WACC: Destroi valor")

st.markdown("---")
st.markdown("Baseado em Aswath Damodaran | Dados: CVM")
