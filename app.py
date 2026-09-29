import streamlit as st

from src.cvm_data import buscar_empresa, carregar_fca_mais_recente


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


@st.cache_data(ttl=86_400)
def carregar_cadastro():
    """Carrega a base mais recente disponível do FCA."""
    return carregar_fca_mais_recente()


try:
    with st.spinner("Carregando cadastro da CVM..."):
        df_cadastro, ano_base = carregar_cadastro()

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

except Exception as erro:
    st.error("Não foi possível carregar ou interpretar os dados da CVM.")
    st.caption(f"Detalhe técnico: {erro}")
