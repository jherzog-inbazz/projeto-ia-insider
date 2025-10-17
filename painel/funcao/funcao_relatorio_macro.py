from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import re
import ast

def app_funcao_relatorio_macro(base_filtrada: pd.DataFrame):
    st.markdown("### Relatório de Publicações")

    # --- Cabeçalho com contagens ---
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

    # 1) URL: criar URL_Status e manter a coluna de link apenas com http(s) ou None
    # Quero tirar o database_url da lista []
    base_filtrada['database_url'] = base_filtrada['database_url'].apply(lambda x: ast.literal_eval(x)[0] if isinstance(x, str) and x.startswith('[') else x)
    
    # 2) Seleção e ordem de colunas
    cols_keep = [
        "post_pk",
        "nome_campanha",
        "post_type",
        "post_date",
        "database_url",
        "URL_Status",
        "Classificação",
        "Justificativa",
        "motivo",
    ]
    # Garante que colunas existam (evita KeyError se vier faltando algo)
    cols_keep = [c for c in cols_keep if c in base_filtrada.columns]
    base_filtrada = base_filtrada[cols_keep].copy()

    # 3) Bullets na Justificativa (sem HTML/Styler)
    def format_justificativa(text):
        if pd.isna(text):
            return text
        frases = re.split(r"\.\s*", str(text))
        frases_formatadas = [f"➔ {f.strip()}" for f in frases if f.strip()]
        return "\n".join(frases_formatadas)

    if "Justificativa" in base_filtrada.columns:
        base_filtrada["Justificativa"] = (
            base_filtrada["Justificativa"].apply(format_justificativa).astype("string")
        )

    # 4) post_pk como inteiro nulo-seguro
    if "post_pk" in base_filtrada.columns:
        base_filtrada["post_pk"] = pd.to_numeric(base_filtrada["post_pk"], errors="coerce").astype("Int64")

    # 5) Emoji de categoria
    emoji_map = {"Aprovado": "✅", "Em Alerta": "⚠️", "Reprovado": "❌"}
    if "Classificação" in base_filtrada.columns:
        base_filtrada["Cat."] = base_filtrada["Classificação"].map(emoji_map).astype("string")
        ordered_cols = ["Cat."] + [c for c in base_filtrada.columns if c != "Cat."]
        base_filtrada = base_filtrada[ordered_cols]


    # Quero que as justificativas dos casos aprovados fiquem em uma letra cinza com transparência
    def style_justificativa(row):
        if row['Classificação'] == 'Aprovado':
            return ['color: rgba(128, 128, 128, 0.7)'] * len(row)
        else:
            return [''] * len(row)
        
    base_filtrada = base_filtrada.style.apply(style_justificativa, axis=1)

    # 6) Exibição (DataFrame puro; nada de .style.apply)
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
            "Cat.": "Cat.",
        },
        hide_index=True,
        use_container_width=True,
        height=560,  # int (evita problemas com 'auto')
    )
