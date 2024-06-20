import streamlit as st
import pandas as pd
from layout_modelagem import inicio, dados_iniciais, coeficientes
from layout_modelagem import fun_contrib_retirad
from equacoes import equacoes_calibragem
from otimizador import algoritimo
import matplotlib.pyplot as plt


def plotar(lista_parametros, lista_coeficientes,
           lista_despejos, lista_retirada, delta):
    st.divider()

    conjunto = [lista_parametros, lista_coeficientes, lista_despejos,
                lista_retirada, delta, 0]

    k2, melhor_aptidao, n_ger = algoritimo(conjunto)
    st.markdown('k2 otimizado: ' + str(k2))
    st.markdown('F1 otimizado: ' + str(melhor_aptidao))
    st.markdown('N° gerações: ' + str(n_ger))

    list_parametros_finais, list_final = equacoes_calibragem(
        lista_parametros, lista_coeficientes, lista_despejos,
        lista_retirada, delta, 0, k2)

    data_1 = {
        'Distância (km)': list_final[0],
        'qr': list_final[1],
        'OD (mg/L)': list_final[2],
        'DBO5 (mg/L)': list_final[3],
        'Coli (NMP/100mL)': list_final[4],
        'N-org (mg/L)': list_final[5],
        'N-amon (mg/L)': list_final[6],
        'N-nitrito (mg/L)': list_final[7],
        'N-nitrato (mg/L)': list_final[8],
        'P-org (mg/L)': list_final[9],
        'P-inorg (mg/L)': list_final[10],
        'N (mg/L)': list_final[11],
        'P (mg/L)': list_final[12]}

    df_final = pd.DataFrame(data_1)

    data_2 = {
        'Parâmetro': ['MÍNIMO', 'MÁXIMO', 'CONAMA'],
        'OD (mg/L)': [min(list_final[2]), max(list_final[2]), '> 5.0'],
        'DBO (mg/L)': [min(list_final[3]), max(list_final[3]), '< 5.0'],
        'N-amon (mg/L)': [min(list_final[6]), max(list_final[6]), '< 3.7'],
        'N-nitrito (mg/L)': [min(list_final[7]), max(list_final[7]), '< 1.0'],
        'N-nitrato (mg/L)': [min(list_final[8]), max(list_final[8]), '< 10.0'],
        'P (mg/L)': [min(list_final[12]), max(list_final[12]), '< 0.1'],
        'Coli (NMP/100mL)': [min(list_final[4]), max(list_final[4]), '< 1000']}

    df_final_parametros = pd.DataFrame(data_2)

    st.markdown('## Resultados')
    st.markdown('k2 otimizado: ' + str(k2))
    st.markdown('F1 otimizado: ' + str(melhor_aptidao))
    st.markdown('N° gerações: ' + str(n_ger))
    st.dataframe(df_final_parametros,
                 hide_index=True,
                 use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.plot(list_final[0], list_final[2])
        plt.xlabel("Comprimento (km)", fontsize=10)
        plt.ylabel("OD (mg/L)", fontsize=10)
        ax.legend()
        plt.title("OD", fontsize=16)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        ax.plot(list_final[0], list_final[3])
        plt.title("OD", fontsize=15)
        plt.xlabel("Comprimento (km)", fontsize=10)
        plt.ylabel("DBO5 (mg/L)", fontsize=10)
        ax.legend()
        plt.title("DBO5", fontsize=16)
        st.pyplot(fig)

    with col1:
        fig, ax = plt.subplots()
        ax.plot(list_final[0], list_final[5], label="N-org (mg/L)")
        ax.plot(list_final[0], list_final[6], label="N-amon (mg/L)")
        ax.plot(list_final[0], list_final[7], label="N-nitrito (mg/L)")
        ax.plot(list_final[0], list_final[8], label="N-nitrato (mg/L)")
        ax.plot(list_final[0], list_final[11], label='N (mg/L)')
        plt.xlabel("Comprimento (km)", fontsize=10)
        plt.ylabel("mg/L", fontsize=10)
        ax.legend()
        plt.title("DBO última", fontsize=16)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        ax.plot(list_final[0], list_final[9], label="P-org (mg/L)")
        ax.plot(list_final[0], list_final[10], label="P-inorg (mg/L)")
        ax.plot(list_final[0], list_final[12], label="P (mg/L)")
        plt.title("P", fontsize=15)
        plt.xlabel("Comprimento (km)", fontsize=10)
        plt.ylabel("mg/L", fontsize=10)
        plt.legend()
        plt.title("P", fontsize=16)
        st.pyplot(fig)

    expander = st.expander("Tabela")
    expander.dataframe(
        df_final, hide_index=True,
        use_container_width=True)

    return


def calibragem(selected, menu):
    # if selected == menu[3]:
    #     st.markdown('#### Modelagem com os coeficientes definidos'
    #                 + ' :orange[manualmente]:')
    #     lista_modelagem, n_trib, delta, labels, lista_tabs, clas_rio = inicio()
    #     lista_parametros = dados_iniciais(lista_modelagem, n_trib,
    #                                       labels, lista_tabs)

    #     lista_coeficientes = coeficientes(lista_modelagem, n_trib,
    #                                       labels, lista_tabs)

    #     lista_retirada = fun_retiradas(
    #         lista_modelagem, n_trib, labels, lista_tabs)

    #     lista_despejos = fun_despejos(lista_modelagem, n_trib,
    #                                   labels, lista_tabs)

    #     # botão
    #     botao = st.button(
    #         'Clique aqui para rodar a modelagem',
    #         type='primary')

    #     if botao:
    #         plotar(lista_parametros, lista_coeficientes,
    #                lista_despejos, lista_retirada, delta)
    return
