from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import re

def app_funcao_relatorio_macro(base_filtrada):
    st.markdown("### Relatório de Publicações")

    with st.container():
        col1, col2 = st.columns([1, 1], border=True)
        with col1:
            total_publicacoes = len(base_filtrada)
            st.markdown(f"###### Total de Publicações Analisadas: **{total_publicacoes}**")
        with col2:
            if "Classificação" in base_filtrada.columns:
                classificacao_counts = base_filtrada["Classificação"].value_counts(dropna=False)
                st.markdown("###### Publicações por Classificação:")
                for classificacao, count in classificacao_counts.items():
                    st.markdown(f"- **{classificacao}**: {count}")

    # --- Normalizações que evitam ArrowInvalid ---

    # 1) URL: manter coluna de link com URL/None e separar um status textual
    base_filtrada["database_url"] = base_filtrada["database_url"].astype("string")

    # marcar status antes de limpar a coluna de link
    url_is_na = base_filtrada["database_url"].isna()
    url_is_empty = base_filtrada["database_url"].str.strip().eq("")  # funciona com dtype string
    base_filtrada["URL_Status"] = np.select(
        [
            url_is_na,          # NaN original
            url_is_empty        # string vazia
        ],
        [
            "Database_Ajust",
            "Database_Null"
        ],
        default="OK"
    )

    # a coluna de link precisa ser URL válida ou None
    base_filtrada["database_url"] = base_filtrada["database_url"].where(
        base_filtrada["database_url"].str.startswith(("http://", "https://"), na=False),
        None
    )

    # 2) selecionar colunas na ordem desejada
    cols_keep = ["post_pk", "nome_campanha", "post_type", "post_date",
                 "database_url", "URL_Status", "Classificação", "Justificativa", "motivo"]
    base_filtrada = base_filtrada[cols_keep]

    # 3) bullets na Justificativa (sem HTML/Styler)
    def format_justificativa(text):
        if pd.isna(text):
            return text
        frases = re.split(r"\.\s*", str(text))
        frases_formatadas = [f"➔ {f.strip()}" for f in frases if f.strip()]
        return "\n".join(frases_formatadas)
    base_filtrada["Justificativa"] = base_filtrada["Justificativa"].apply(format_justificativa).astype("string")

    # 4) post_pk como inteiro nulo-seguro (evita erro de tipo)
    base_filtrada["post_pk"] = pd.to_numeric(base_filtrada["post_pk"], errors="coerce").astype("Int64")

    # 5) emoji de categoria
    emoji_map = {"Aprovado": "✅", "Em Alerta": "⚠️", "Reprovado": "❌"}
    base_filtrada["Cat."] = base_filtrada["Classificação"].map(emoji_map).astype("string")

    # reordenar com Cat. primeiro
    ordered_cols = ["Cat."] + [c for c in base_filtrada.columns if c != "Cat."]
    base_filtrada = base_filtrada[ordered_cols]

    # 6) Nada de .style.apply aqui (Styler pode quebrar a conversão Arrow).
    #    Se quiser "cinza" para Aprovado, recomendo mostrar isso numa coluna auxiliar
    #    (ex.: prefixo "[Aprovado]" na Justificativa) — Streamlit não aplica cor por célula no dataframe sem Styler.

    st.dataframe(
        base_filtrada,
        column_config={
            "post_pk": st.column_config.TextColumn("ID da Publicação"),
            "nome_campanha": "Nome da Campanha",
            "post_type": "Tipo de Publicação",
            "post_date": "Data e Horário da Publicação",
            "database_url": st.column_config.LinkColumn("URL", display_text="Link da Publicação"),
            "URL_Status": "Status da URL",
            "Classificação": "Classificação do Modelo",
            "Justificativa": st.column_config.TextColumn(label="Justificativa do Modelo", width=600),
            "motivo": "Motivo",
            "Cat.": "Cat."
        },
        hide_index=True,
        use_container_width=True,
        height=560  # use int; "auto" pode causar comportamento inesperado
    )
