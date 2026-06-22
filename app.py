def buscar_dados_financeiros(cnpj, arquivo_zip_dfp):
    nome_arquivo_bpp = f"dfp_cia_aberta_BPP_con_2025.csv"
    with arquivo_zip_dfp.open(nome_arquivo_bpp) as f:
        df_bpp = pd.read_csv(f, sep=";", encoding="latin-1")
    
    # Debug: mostra quais CNPJs estão no arquivo
    cnpjs_unicos = df_bpp["CNPJ_CIA"].unique()
    st.write(f"DEBUG: Total de CNPJs no arquivo: {len(cnpjs_unicos)}")
    st.write(f"DEBUG: CNPJ procurado: {cnpj}")
    st.write(f"DEBUG: CNPJ está no arquivo? {cnpj in cnpjs_unicos}")
    
    # Tenta sem formatacao
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")
    st.write(f"DEBUG: CNPJ limpo: {cnpj_limpo}")
    
    # Filtra
    df_bpp_filtrado = df_bpp[df_bpp["CNPJ_CIA"] == cnpj]
    st.write(f"DEBUG: Linhas encontradas com CNPJ exato: {len(df_bpp_filtrado)}")
    
    # Se não encontrou, tenta sem formatação
    if len(df_bpp_filtrado) == 0:
        df_bpp_filtrado = df_bpp[df_bpp["CNPJ_CIA"].str.replace(".", "").str.replace("/", "").str.replace("-", "") == cnpj_limpo]
        st.write(f"DEBUG: Linhas encontradas com CNPJ limpo: {len(df_bpp_filtrado)}")
    
    # Mostra os períodos disponíveis
    if len(df_bpp_filtrado) > 0:
        periodos = df_bpp_filtrado["ORDEM_EXERC"].unique()
        st.write(f"DEBUG: Periodos disponiveis: {periodos}")
        df_bpp_filtrado = df_bpp_filtrado[df_bpp_filtrado["ORDEM_EXERC"] == "ULTIMO"]
    
    nome_arquivo_bpa = f"dfp_cia_aberta_BPA_con_2025.csv"
    with arquivo_zip_dfp.open(nome_arquivo_bpa) as f:
        df_bpa = pd.read_csv(f, sep=";", encoding="latin-1")
    df_bpa = df_bpa[(df_bpa["CNPJ_CIA"] == cnpj) & (df_bpa["ORDEM_EXERC"] == "ULTIMO")]
    
    nome_arquivo_dre = f"dfp_cia_aberta_DRE_con_2025.csv"
    with arquivo_zip_dfp.open(nome_arquivo_dre) as f:
        df_dre = pd.read_csv(f, sep=";", encoding="latin-1")
    df_dre = df_dre[(df_dre["CNPJ_CIA"] == cnpj) & (df_dre["ORDEM_EXERC"] == "ULTIMO")]
    
    return {"bpa": df_bpa, "bpp": df_bpp_filtrado, "dre": df_dre}
