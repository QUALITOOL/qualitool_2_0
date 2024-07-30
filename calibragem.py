import streamlit as st
from layout_modelagem import inicio, dados_iniciais, coeficientes
from layout_modelagem import fun_contrib_retirad, salvararquivo
from resultados import transformacao, resultados, plotar
import copy


def calibragem(selected, menu):
    if selected == menu[3]:
        st.markdown('#### Modelagem com os'
                    + ' :orange[coeficientes otimizados por Inteligência computacional (IC)]:')
        
        st.markdown('#### :red[EM MANUTENÇÃO...]')

        paramentro = [True, False, True, True, True, True, 0, True]
        lista_modelagem, data, labels, lista_tabs = inicio(paramentro)
        n_trib = lista_modelagem[6]


        lista_parametros, list_name, list_valores, zona, hemisferio, dias = dados_iniciais(data, lista_modelagem, n_trib,
                                        labels, lista_tabs)
        
        list_name_salvo = copy.deepcopy(list_name)
        ponto_af = lista_parametros[8]
        ordem_desague = lista_parametros[9]



        lista_contr_retir = fun_contrib_retirad(data, n_trib, labels, lista_tabs, list_name, list_valores, lista_modelagem, dias)


    return