import streamlit as st
from PIL import Image


st.markdown('''<h3 style='text-align: center;
            color: teal;
            '>Apresentação </h3>''',
            unsafe_allow_html=True)

st.markdown('''<div style='text-align: justify;
            '><b>QUALITOOL 2.0</b> é uma ferramenta de simulação 
            computacional otimizada para o desenvolvimento de 
            Sistemas de Apoio à Decisão (SSD) para o planejamento 
            de gestão de qualidade de água em ambientes lóticos. 
            </div>''',
            unsafe_allow_html=True)
st.write('')
st.markdown('''<div style='text-align: justify;
            '>A versão 2.0 do QUALITOOL foi desenvolvida como 
            parte de um projeto de pesquisa de mestrado pela 
            <b>Ma. Flavya Fernanda França Vilela¹</b> e pelo 
            professor <b>Dr. Márcio Ricardo Salla²</b>, 
            ambos vinculados ao Programa de Pós-Graduação em 
            Qualidade Ambiental (PPGMQ) da Universidade Federal 
            de Uberlândia - UFU. 
            O projeto recebeu apoio financeiro da Fundação de 
            Amparo à Pesquisa do Estado de Minas (Fapemig). 
            </div>''',
            unsafe_allow_html=True)
st.write('')
st.markdown('''<div style='text-align: justify;
            '>Esta plataforma é disponibilizada de forma gratuita 
            com o objetivo de contribuir para a comunidade. Os 
            autores não assumem responsabilidade por eventuais 
            erros no programa, mas ficam gratos pela comunicação 
            de qualquer problema identificado.</div>''',
            unsafe_allow_html=True)
st.write('')
st.write('')
st.write('')
st.markdown('''<div style='text-align: justify;
            '>¹ Mestre em Qualidade Ambiental pela Universidade 
            Federal de Uberlândia (2025). </div>''',
            unsafe_allow_html=True)
st.markdown('''<div style='text-align: justify;
            '>² Doutor em Engenharia Hidráulica e Saneamento pela 
            Universidade de São Paulo (2006); Pós-doutorado pelo 
            Instituto de Ingeniería del Agua y Medio Ambiente de 
            la Universidad Politecnica de Valencia - 
            IIAMA/UPV (2013).  </div>''',
            unsafe_allow_html=True)
st.write('')
st.markdown('''Contatos: qualitool.labhidro.ufu@gmail.com | 
            flavya2310@gmail.com | marcio.salla@ufu.br
            ''')

st.write("   ")

st.markdown('<h6 style="text-align: right;">Apoio:</h6>',
            unsafe_allow_html=True)

# imagem_1 = Image.open(r'C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\Meu_rep\imagens\logos_geral.png')
imagem_1 = Image.open('imagens/logos_geral.png')
st.image(imagem_1, output_format="PNG")

