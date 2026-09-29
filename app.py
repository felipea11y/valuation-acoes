from datetime import datetime

import streamlit as st

from src.cvm_data import (
    buscar_empresa,
    carregar_demonstracao,
    carregar_fca_mais_recente,
    colunas_exibicao_demonstracao,
    filtrar_demonstracao_empresa,
)


st.set_page_config(
    page_title="Valuation de Ações",
    page_icon="📊",
    layout="wide",
)

st.title("Analisador de Ações Brasileiras")
st.caption(
    "Protótipo acadêmico com dados públicos da CVM para identificação "
    "de companhias e leitura inicial de demonstrações financeiras."
)


@st.cache_data(ttl=86_400)
def carregar_cadastro():
    return carregar_fca_mais_recente()


@st.cache_data(ttl=86_400)
def carregar_dados_contabeis(documento: str, demonstracao: str, ano: int):
    return carregar_demonstracao(documento, demonstracao, ano)


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
            nome = str(empresa["Nome_Empresarial"])
            cnpj = str(empresa["CNPJ_Companhia"])

            st.subheader(nome)
            st.write(f"**Ticker:** {ticker.strip().upper()}")
            st.write(f"**CNPJ:** {cnpj}")

            if len(resultado) > 1:
                st.caption(
                    f"O ticker possui {len(resultado)} registros na tabela consultada; "
                    "o primeiro foi usado para esta visualização."
                )

            st.divider()
            st.subheader("Demonstrações financeiras")

            col1, col2, col3 = st.columns(3)

            with col1:
                documento = st.selectbox("Documento", ["DFP", "ITR"])

            with col2:
                demonstracao = st.selectbox("Demonstração", ["DRE", "BPP", "BPA"])

            with col3:
                ano_padrao = datetime.now().year - 1 if documento == "DFP" else datetime.now().year
                ano = st.number_input(
                    "Ano",
                    min_value=2011,
                    max_value=datetime.now().year,
                    value=ano_padrao,
                    step=1,
                )

            if st.button("Carregar demonstração"):
                with st.spinner(
                    f"Carregando {documento} {demonstracao} de {int(ano)}..."
                ):
                    df_demonstracao = carregar_dados_contabeis(
                        documento,
                        demonstracao,
                        int(ano),
                    )

                df_empresa = filtrar_demonstracao_empresa(
                    df_demonstracao,
                    cnpj,
                )

                if df_empresa.empty:
                    st.warning(
                        "Não foram encontrados dados consolidados para essa "
                        "companhia, demonstração e ano."
                    )
                else:
                    colunas = colunas_exibicao_demonstracao(df_empresa)
                    st.dataframe(
                        df_empresa[colunas].reset_index(drop=True),
                        use_container_width=True,
                    )
                    st.caption(
                        "Valores exibidos diretamente da demonstração estruturada "
                        "da CVM. Nenhum cálculo de valuation é aplicado nesta etapa."
                    )

            st.info(
                "Etapa atual: leitura de dados cadastrais e demonstrações financeiras. "
                "Indicadores fundamentalistas e valuation ainda serão implementados."
            )
        else:
            st.warning("Ticker não encontrado no cadastro consultado da CVM.")

    st.markdown(
        "Fontes: [FCA](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca), "
        "[DFP](https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp) e "
        "[ITR](https://dados.cvm.gov.br/dataset/cia_aberta-doc-itr)."
    )

except Exception as erro:
    st.error("Não foi possível carregar ou interpretar os dados da CVM.")
    st.caption(f"Detalhe técnico: {erro}")
