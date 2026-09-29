from datetime import datetime

import streamlit as st

from src.cvm_data import (
    buscar_empresa,
    carregar_demonstracao,
    carregar_fca_mais_recente,
    colunas_exibicao_demonstracao,
    filtrar_demonstracao_empresa,
)
from src.indicadores import (
    calcular_indicadores_dre,
    montar_serie_historica_dre,
    resumo_crescimento_historico,
)


st.set_page_config(
    page_title="Valuation de Ações",
    page_icon="📊",
    layout="wide",
)

st.title("Analisador de Ações Brasileiras")
st.caption(
    "Protótipo acadêmico com dados públicos da CVM para identificação, "
    "demonstrações financeiras e indicadores descritivos."
)


@st.cache_data(ttl=86_400)
def carregar_cadastro():
    return carregar_fca_mais_recente()


@st.cache_data(ttl=86_400)
def carregar_dados_contabeis(documento: str, demonstracao: str, ano: int):
    return carregar_demonstracao(documento, demonstracao, ano)


def formatar_valor(valor: float | None) -> str:
    if valor is None:
        return "N/D"
    return f"{valor:,.0f}".replace(",", ".")


def formatar_percentual(valor: float | None) -> str:
    if valor is None:
        return "N/D"
    return f"{valor * 100:.1f}%".replace(".", ",")


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
                ano_padrao = (
                    datetime.now().year - 1
                    if documento == "DFP"
                    else datetime.now().year
                )
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
                    if demonstracao == "DRE":
                        indicadores = calcular_indicadores_dre(df_empresa)

                        st.markdown("#### Indicadores da DRE")
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Receita", formatar_valor(indicadores["receita"]))
                        m2.metric(
                            "Resultado operacional",
                            formatar_valor(indicadores["resultado_operacional"]),
                        )
                        m3.metric(
                            "Lucro líquido",
                            formatar_valor(indicadores["lucro_liquido"]),
                        )
                        m4.metric(
                            "Margem líquida",
                            formatar_percentual(indicadores["margem_liquida"]),
                        )

                        n1, n2, n3 = st.columns(3)
                        n1.metric(
                            "Margem bruta",
                            formatar_percentual(indicadores["margem_bruta"]),
                        )
                        n2.metric(
                            "Margem operacional",
                            formatar_percentual(indicadores["margem_operacional"]),
                        )
                        n3.metric(
                            "Resultado bruto",
                            formatar_valor(indicadores["resultado_bruto"]),
                        )

                        st.caption(
                            "Os valores monetários permanecem na escala informada "
                            "pela base estruturada da CVM. As margens são razões "
                            "calculadas sobre a receita."
                        )

                    colunas = colunas_exibicao_demonstracao(df_empresa)
                    st.markdown("#### Linhas da demonstração")
                    st.dataframe(
                        df_empresa[colunas].reset_index(drop=True),
                        use_container_width=True,
                    )
                    st.caption(
                        "Valores contábeis obtidos da demonstração estruturada "
                        "da CVM. Nenhum cálculo de valuation é aplicado nesta etapa."
                    )

            st.divider()
            st.subheader("Série histórica anual")
            st.caption(
                "Usa DFPs anuais consolidadas. A consulta é limitada a cinco "
                "exercícios por vez para evitar downloads excessivos."
            )

            ultimo_ano_fechado = datetime.now().year - 1
            h1, h2 = st.columns(2)

            with h1:
                ano_inicial = st.number_input(
                    "Ano inicial",
                    min_value=2011,
                    max_value=ultimo_ano_fechado,
                    value=max(2011, ultimo_ano_fechado - 2),
                    step=1,
                    key="historico_inicio",
                )

            with h2:
                ano_final = st.number_input(
                    "Ano final",
                    min_value=2011,
                    max_value=ultimo_ano_fechado,
                    value=ultimo_ano_fechado,
                    step=1,
                    key="historico_fim",
                )

            if st.button("Carregar série histórica"):
                inicio = int(ano_inicial)
                fim = int(ano_final)

                if fim < inicio:
                    st.error("O ano final deve ser maior ou igual ao ano inicial.")
                elif fim - inicio + 1 > 5:
                    st.error("Selecione no máximo cinco exercícios por consulta.")
                else:
                    demonstracoes = {}

                    with st.spinner(
                        f"Carregando DREs anuais de {inicio} a {fim}..."
                    ):
                        for ano_hist in range(inicio, fim + 1):
                            df_ano = carregar_dados_contabeis("DFP", "DRE", ano_hist)
                            empresa_ano = filtrar_demonstracao_empresa(df_ano, cnpj)

                            if not empresa_ano.empty:
                                demonstracoes[ano_hist] = empresa_ano

                    serie = montar_serie_historica_dre(demonstracoes)

                    if serie.empty:
                        st.warning(
                            "Não foram encontrados dados anuais para o período selecionado."
                        )
                    else:
                        resumo = resumo_crescimento_historico(serie)

                        c1, c2 = st.columns(2)
                        c1.metric(
                            "CAGR da receita",
                            formatar_percentual(resumo["cagr_receita"]),
                        )
                        c2.metric(
                            "CAGR do lucro líquido",
                            formatar_percentual(resumo["cagr_lucro"]),
                        )

                        tabela = serie[
                            [
                                "ano",
                                "receita",
                                "lucro_liquido",
                                "margem_operacional",
                                "margem_liquida",
                                "crescimento_receita",
                                "crescimento_lucro",
                            ]
                        ].copy()

                        st.dataframe(
                            tabela,
                            use_container_width=True,
                            hide_index=True,
                        )

                        st.line_chart(
                            serie.set_index("ano")[["receita", "lucro_liquido"]]
                        )
                        st.caption(
                            "CAGR só é calculado quando os valores inicial e final "
                            "são positivos. Crescimento histórico não é projeção futura."
                        )

            st.info(
                "Etapa atual: dados cadastrais, demonstrações financeiras, "
                "indicadores e séries históricas. Valuation ainda não está implementado."
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
