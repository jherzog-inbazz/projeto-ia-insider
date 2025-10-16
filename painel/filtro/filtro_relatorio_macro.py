from PIL import Image
import streamlit as st
import pandas as pd
import re
import ast

def app_filtro_relatorio_macro():

    # Importar a base em formato json
    df = pd.read_json('data/data_insider.json')

    # Filtrar casos em que a cod_ident não é nulo
    df = df[df['cod_ident'].notna()]

    base_filtrada = df.copy()

    return base_filtrada