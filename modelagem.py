import streamlit as st
from layout_modelagem import inicio, dados_iniciais, coeficientes
from layout_modelagem import fun_contrib_retirad, salvararquivo
from resultados import transformacao, resultados, plotar
import copy


def modelagem(selected, menu):
    if selected == menu[2]:
        st.markdown('#### Modelagem com os'
                    + ' :orange[coeficientes predefinidos]:')

        paramentro = {'m_od': True, 'm_dbo': True, 'm_n': True, 'm_p': True,
                      'm_c': True, 'n_tb': 0, 's_t': True}
        lista_modelagem, data, labels, lista_tabs = inicio(paramentro)
        n_trib = lista_modelagem['n_tb']


        lista_parametros, list_name, list_valores, zona, hemisferio, dias = dados_iniciais(data, lista_modelagem, n_trib,
                                        labels, lista_tabs)
        
        list_name_salvo = copy.deepcopy(list_name)
        ponto_af = lista_parametros['p_af']
        ordem_desague = lista_parametros['l_des']

        lista_coeficientes = coeficientes(data, lista_modelagem, n_trib,
                                        labels, lista_tabs, dias)

        lista_contr_retir = fun_contrib_retirad(data, n_trib, labels, lista_tabs, list_name, list_valores, lista_modelagem, dias)

        salvararquivo(lista_modelagem, lista_parametros, lista_coeficientes, lista_contr_retir, list_name_salvo, list_valores)


        # botão
        botao = st.button(
            'Clique aqui para iniciar a modelagem',
            type='primary')

        if botao:
            list_tranfor = transformacao(lista_modelagem, lista_parametros, lista_coeficientes,
                                        lista_contr_retir, list_name_salvo)
            
            lidt_df, list_entr, ordem_modelagem  = resultados(n_trib, list_tranfor, ponto_af, lista_modelagem, ordem_desague, dias)

            plotar(n_trib, lista_modelagem, lidt_df, list_entr, labels, zona, hemisferio, dias, ordem_modelagem)

            
    return
