# streamlit run C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\QT_2.py
import streamlit as st
from streamlit_option_menu import option_menu
from introducao import introducao
from modelagem import modelagem
from calibragem import calibragem
from instrucoes import teste
import streamlit as st

from PIL import Image

#opening the image
image = Image.open('LOGO.png')

bar = st.sidebar
bar.image(image, output_format="PNG")
bar.markdown('##### **:blue[MODELO DE QUALIDADE DA ÁGUA DE RIOS]**')
bar.markdown('## **:red[EM MANUTENÇÃO...]**')

# 1. as sidebar menu
menu = ["INICÍO", 'INSTRUÇÕES', "MODELAGEM",  "CALIBRAÇÃO"]
with st.sidebar:
    selected = option_menu(None, menu,
                           icons=[
                               'house', 'gear', "list-task", 'cloud-upload'],
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