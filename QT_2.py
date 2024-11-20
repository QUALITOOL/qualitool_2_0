# streamlit run C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\QT_2.py
import streamlit as st
from streamlit_option_menu import option_menu
from introducao import introducao
from modelagem import modelagem
from calibragem import calibragem
from graficos import plotagem
from instrucoes import teste
import streamlit as st

from PIL import Image

#opening the image
# image = Image.open('C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\LOGO.png')
image = Image.open('LOGO.png')

bar = st.sidebar
bar.image(image, output_format="PNG")
bar.text(' ')
bar.markdown('''<div style='text-align: center;
                    color: teal;
                    '>MODELO DE QUALIDADE DA ÁGUA </div>''',
                    unsafe_allow_html=True)
bar.text(' ')

# 1. as sidebar menu
menu = ["APRESENTAÇÃO", 'INSTRUÇÕES', "MODELAGEM",  "AJUSTE E CALIBRAÇÃO", "GRÁFICOS"]
with st.sidebar:
    selected = option_menu(None, menu,
                           icons=[
                               'house', 'list-task', "gear", 'bezier', 'graph-up'],
                           default_index=0,
                           styles={
                               "container": {"padding": "0!important"},
                               "icon": {
                                   "color": "orange", "font-size": "18px"},
                               "nav-link": {
                                   "font-size": "18px", "margin": "0px"},
                               "nav-link-selected": {
                                   "background-color": "teal"},
                           })

introducao(selected, menu)
teste(selected, menu)
modelagem(selected, menu)
calibragem(selected, menu)
plotagem(selected, menu)
