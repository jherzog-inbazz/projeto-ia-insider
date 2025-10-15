from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def categorizar_post(row):
    """
    Função para categorizar a publicação com base nas variáveis de legenda.
    """
    
    # Verificar se há CTA (legenda_possibilities_cta)
    cta = row.get('legenda_possibilities_cta', None)
    ai_probability = row.get('legenda_ai_probability', 0)
    principios = row.get('legenda_product_principles', None)
    
    # Caso "Ruim": se houver CTA, probabilidade de IA maior ou igual a 0.5, ou princípios da marca ausentes
    if cta is not None or ai_probability >= 0.5:
        if principios is None:
            return 'Ruim'
    
    # Condição para categoria "Intermediária"
    sentiment_score = row.get('legenda_sentiment_score', 0)
    product_principles_categories = len(principios) if isinstance(principios, list) else 0
    triggers = row.get('legenda_triggers', [])
    triggers_categories = len(triggers) if isinstance(triggers, list) else 0
    
    # Para ser "Intermediária", o sentimento deve ser negativo (menor que 0.7),
    # deve ter no máximo uma categoria em 'legenda_product_principles' e no máximo uma em 'legenda_triggers'.
    if sentiment_score < 0.7 and product_principles_categories <= 1 and triggers_categories <= 1:
        return 'Intermediária'
    
    # Condição para categoria "Boa"
    # Para ser "Boa", o sentimento deve ser positivo (maior ou igual a 0.7),
    # deve ter mais de uma categoria em 'legenda_product_principles' e mais de uma em 'legenda_triggers'.
    if sentiment_score >= 0.7 and product_principles_categories > 1 and triggers_categories > 1:
        return 'Boa'

    # Se não se encaixar nas condições acima, categoriza como "Ruim"
    return 'Intermediária'




def app_funcao_relatorio_macro(base_filtrada):

    # Selecionar as variáveis de interesse
    variaveis_interesse = [
        'cod_ident',
        'post_type',
        'post_date',
        'post_url',
        'nome_campanha',
        'imagem_hashtags',
        'imagem_mentions',
        'imagem_urls',
        'imagem_emoticoins',
        'imagem_coupon_codes',
        'imagem_seller_codes',
        'imagem_types_products',
        'imagem_product_focus_image',
        'imagem_category',
        'imagem_triggers',
        'imagem_possibilities_cta',
        'imagem_sentiment_score',
        'legenda_hashtags',
        'legenda_mentions',
        'legenda_urls',
        'legenda_emoticoins',
        'legenda_coupon_codes',
        'legenda_seller_codes',
        'legenda_category',
        'legenda_triggers',
        'legenda_possibilities_cta',
        'legenda_sentiment_score',
        'legenda_emotion',
        'legenda_style_metrics',
        'legenda_style_description',
        'legenda_target_audience_age',
        'legenda_suggested_improvements',
        'legenda_is_ai_generated',
        'legenda_evidence',
        'legenda_style_characteristics',
        'legenda_ai_probability',
        'legenda_overall_classification',
        'legenda_product_principles'
    ]

    # Criar um DataFrame com as variáveis selecionadas
    base_filtrada = base_filtrada[variaveis_interesse].copy()

    base_filtrada['categoria'] = base_filtrada.apply(categorizar_post, axis=1)

    # Selecionar as variáveis de interesse
    variaveis_interesse = [
        'cod_ident',
        'nome_campanha',
        'post_type',
        'post_date',
        'post_url',
        'categoria'
    ]

    # Criar um DataFrame com as variáveis selecionadas
    base_filtrada = base_filtrada[variaveis_interesse].copy()

    # Exibir o DataFrame no Streamlit com formatação
    st.markdown("### Relatório de Publicações")

    st.dataframe(
        base_filtrada,
        column_config={
            "cod_ident": 'ID da Publicação',
            'nome_campanha': 'Nome da Campanha',
            'post_type': 'Tipo de Publicação',
            'post_date': 'Data e Horário da Publicação',
            "post_url": st.column_config.LinkColumn("URL"),
            'categoria': 'Categoria',
        },
        hide_index=True,
        use_container_width=True
    )