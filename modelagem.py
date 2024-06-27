import streamlit as st
from layout_modelagem import inicio, dados_iniciais, coeficientes
from layout_modelagem import fun_contrib_retirad, salvararquivo
from resultados import transformacao, resultados, plotar


def modelagem(selected, menu):
    if selected == menu[2]:
        st.markdown('#### Modelagem com os coeficientes definidos'
                    + ' :orange[manualmente]:')

        paramentro = [True, False, True, True, True, True, 0]
        lista_modelagem, data, labels, lista_tabs = inicio(paramentro)
        n_trib = lista_modelagem[-1]


        lista_parametros, list_name, list_valores, zona, hemisferio = dados_iniciais(data, lista_modelagem, n_trib,
                                        labels, lista_tabs)
        ponto_af = lista_parametros[-1]

        lista_coeficientes = coeficientes(data, lista_modelagem, n_trib,
                                        labels, lista_tabs)

        lista_contr_retir = fun_contrib_retirad(data, n_trib, labels, lista_tabs, list_name, list_valores)

        salvararquivo(lista_modelagem, lista_parametros, lista_coeficientes, lista_contr_retir, list_name, list_valores)


        # botão
        botao = st.button(
            'Clique aqui para rodar a modelagem',
            type='primary')

        if botao:
            list_tranfor = transformacao(lista_modelagem, lista_parametros, lista_coeficientes,
                                        lista_contr_retir, list_name)
            
            lidt_df, list_entr  = resultados(n_trib, list_tranfor, ponto_af, lista_modelagem)

            plotar(n_trib, lista_modelagem, lidt_df, list_entr, labels, zona, hemisferio)

            
    return
