from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def app_funcao_relatorio_macro(base_filtrada):

    # Exibir o DataFrame no Streamlit com formatação
    st.markdown("### Relatório de Publicações")

    # Selecionar as variáveis específicas
    base_filtrada = base_filtrada[
        ["cod_ident", "nome_campanha", "post_type", "post_date", "post_url", "Classificação", "Justificativa"]
        ]
    

    st.dataframe(
        base_filtrada,
        column_config={
            "cod_ident": 'ID da Publicação',
            'nome_campanha': 'Nome da Campanha',
            'post_type': 'Tipo de Publicação',
            'post_date': 'Data e Horário da Publicação',
            "post_url": st.column_config.LinkColumn("URL"),
            "Classificação":"Classificação do Modelo",
            "Justificativa":"Justificativa do Modelo"
        },
        hide_index=True,
        use_container_width=True
    )