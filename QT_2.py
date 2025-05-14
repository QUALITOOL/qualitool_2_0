# streamlit run C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\Meu_rep\QT_2.py
import streamlit as st
from PIL import Image


pg = st.navigation([st.Page("pages/introducao.py",
                            title="QUALITOOL 2.0"),
                    st.Page("pages/instrucoes.py",
                            title="QUALITOOL-Instruções"),
                    st.Page("pages/modelagem.py",
                            title="QUALITOOL-Modelagem"),
                    st.Page("pages/calibragem.py",
                            title="QUALITOOL-Ajuste"),
                    st.Page("pages/graficos.py",
                            title="QUALITOOL-Gráficos"),
                    st.Page("pages/resultados_model.py",
                            title="QUALITOOL-Modelagem-Resultados"),
                    st.Page("pages/resultados_calib.py",
                            title="QUALITOOL-Ajuste-Resultados"),
                    st.Page("pages/resultados_calib_as.py",
                            title="QUALITOOL-Ajuste-Resultados"),
                    st.Page("pages/resultados_calib_pso.py",
                            title="QUALITOOL-Ajuste-Resultados")],
                    position="hidden")

# image = Image.open('C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\Meu_rep\imagens\LOGO.png')
image = Image.open('imagens/LOGO.png')

bar = st.sidebar
bar.image(image)
bar.text(' ')
bar.markdown('''<div style='text-align: center;
                    color: teal;
                    '>MODELAGEM DE QUALIDADE DA ÁGUA </div>''',
                    unsafe_allow_html=True)
bar.text(' ')

bar.page_link("pages/introducao.py", label="APRESENTAÇÃO",
              icon=":material/home:")
bar.page_link("pages/instrucoes.py", label="INSTRUÇÕES",
              icon=":material/data_table:")
bar.page_link("pages/modelagem.py", label="MODELAGEM",
              icon=":material/trending_up:")
bar.page_link("pages/calibragem.py", label="AJUSTE E CALIBRAÇÃO",
              icon=":material/hub:")
bar.page_link("pages/graficos.py", label="GRÁFICOS",
              icon=":material/bar_chart_4_bars:")


pg.run()



