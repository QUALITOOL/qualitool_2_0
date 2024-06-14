import streamlit as st
import pandas as pd
from io import StringIO


def teste(selecao, menu):
    if selecao == menu[1]:
        st.markdown('''<h1 style='text-align: center;
                    color: teal;
                    '>Teste </h2>''',
                    unsafe_allow_html=True)

        uploaded_file = st.file_uploader("TESTE")
        if uploaded_file is not None:
            dataframe = pd.read_excel(uploaded_file)
            st.write(dataframe)

    return