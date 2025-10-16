from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def app_funcao_relatorio_macro(base_filtrada):

    # Exibir o DataFrame no Streamlit com formatação
    st.markdown("### Relatório de Publicações")

    with st.container():
        col1, col2 = st.columns([1, 1], border=True)

        with col1:
            # Quantidade de publicações analisadas
            total_publicacoes = base_filtrada.shape[0]
            st.markdown(
                f"""
                ###### Total de Publicações Analisadas: **{total_publicacoes}**
                """
            )

        with col2:
            # Quantidade de publicações pelo tipo de classificação
            classificacao_counts = base_filtrada['Classificação'].value_counts()
            st.markdown("###### Publicações por Classificação:")
            for classificacao, count in classificacao_counts.items():
                st.markdown(f"- **{classificacao}**: {count}")


    # Quero tirar o database_url da lista []
    base_filtrada['database_url'] = base_filtrada['database_url'].apply(lambda x: ast.literal_eval(x)[0] if isinstance(x, str) and x.startswith('[') else x)


    # Selecionar as variáveis específicas
    base_filtrada = base_filtrada[
        ["post_pk", "nome_campanha", "post_type", "post_date", "database_url", "Classificação", "Justificativa"]
        ]
    

    # Quero que as justificativas fiquem em formato de tópicos a cada . e colocar uma setinha antes de cada tópico
    def format_justificativa(text):
        if pd.isna(text):
            return text
        # Dividir o texto em frases usando regex para considerar pontos seguidos de espaço ou fim de linha
        frases = re.split(r'\.\s*', text)
        # Adicionar uma seta antes de cada frase e remover frases vazias
        frases_formatadas = [f"➔ {frase.strip()}" for frase in frases if frase.strip()]
        # Juntar as frases formatadas com quebras de linha
        return "\n".join(frases_formatadas)
    base_filtrada['Justificativa'] = base_filtrada['Justificativa'].apply(format_justificativa)

    # Agora você pode aplicar o astype sem problemas
    base_filtrada['post_pk'] = base_filtrada['post_pk'].astype(int)

    # Retirar o dabaser_url da lista []
    base_filtrada['database_url'] = base_filtrada['database_url'].apply(lambda x: x if isinstance(x, str) else str(x))

    # Mapeando as classificações para emojis
    emoji_map = {
        'Aprovado': '✅',
        'Em Alerta': '⚠️',
        'Reprovado': '❌'
    }

    # Aplicando os emojis à coluna 'Classificação'
    base_filtrada['Cat.'] = base_filtrada['Classificação'].map(emoji_map)

    # Selecionar as variáveis específicas
    base_filtrada = base_filtrada[
        ["Cat.","post_pk", "nome_campanha", "post_type", "post_date", "database_url", "Classificação", "Justificativa"]
        ]

    # Quero que as justificativas dos casos aprovados fiquem em uma letra cinza com transparência
    def style_justificativa(row):
        if row['Classificação'] == 'Aprovado':
            return ['color: rgba(128, 128, 128, 0.7)'] * len(row)
        else:
            return [''] * len(row)
        
    base_filtrada = base_filtrada.style.apply(style_justificativa, axis=1)


    st.dataframe(
        base_filtrada,
        column_config={
            'Cat.': 'Cat.',
            "post_pk": st.column_config.TextColumn("ID da Publicação"),
            "nome_campanha": 'Nome da Campanha',
            "post_type": 'Tipo de Publicação',
            "post_date": 'Data e Horário da Publicação',
            "database_url": st.column_config.LinkColumn("URL", display_text="Link da Publicação"),
            "Classificação": "Classificação do Modelo",
            "Justificativa": st.column_config.TextColumn(label="Justificativa do Modelo", width=600)
        },
        hide_index=True,
        use_container_width=True,
        height='auto'  # Ajusta o valor da altura da tabela
    )