import streamlit as st


st.markdown('''<h3 style='text-align: center;
            color: teal;
            '>Instruções e dicas</h3>''',
            unsafe_allow_html=True)

st.write(' ')
st.write(' ')
st.markdown('''<div style='text-align: justify;
            '>Mensagem de texto para instruir o usuário.</div>''',
            unsafe_allow_html=True)

st.write(' ')
st.page_link("https://github.com/QUALITOOL/qualitool_2_0", label="Repositório no GITHUB", icon=":material/code:")
st.page_link("https://labsanufu.wixsite.com/site", label="Visite o site do LABSAN", icon=":material/find_in_page:")

st.divider()
st.markdown('''<h5 style='text-align: center;
            color: teal;
            '>Manuais</h5>''',
            unsafe_allow_html=True)

# munual_qt1 = "C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\Meu_rep\documentos\qt1_manual.pdf"
munual_qt1 = "documentos/qt1_manual.pdf"


with open(munual_qt1, "rb") as file:
    pdf_qt1_manual = file.read()

st.write(' ')

col1, col2 = st.columns(2)
col1.download_button(
    label="QT1 - MANUAL DO USUÁRIO",
    data=pdf_qt1_manual,
    file_name="qt1_manual.pdf",
    use_container_width=True
)

st.divider()

st.markdown('''<h5 style='text-align: center;
            color: teal;
            '>Exemplos resolvidos</h5>''',
            unsafe_allow_html=True)

# exemplo_qt1 = "C:\Flavya\MQA\QUALI_TOOL\QT_2_0\qualitool_local\Meu_rep\documentos\qt1_exemplo_pratico.pdf"
exemplo_qt1 = "documentos/qt1_exemplo_pratico.pdf"

with open(exemplo_qt1, "rb") as file:
    pdf_qt1_ex = file.read()

st.write(' ')
col_1, col_2 = st.columns(2)

col_1.download_button(
    label="QT1 - EXEMPLO PRÁTICO",
    data=pdf_qt1_ex,
    file_name="qt1_exemplo_pratico.pdf",
    use_container_width=True
)


st.divider()