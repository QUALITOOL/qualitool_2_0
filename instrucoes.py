import streamlit as st
from PIL import Image


def teste(selecao, menu):
    if selecao == menu[1]:
        
        st.markdown('''<h3 style='text-align: center;
                    color: teal;
                    '>Instruções </h3>''',
                    unsafe_allow_html=True)
        
        st.markdown('''<div style='text-align: justify;
                    '>Em manutenção.  </div>''',
                    unsafe_allow_html=True)
    return