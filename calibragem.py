import streamlit as st
from layout_modelagem import inicio, dados_iniciais, coeficientes
from layout_modelagem import fun_contrib_retirad, salvararquivo
from resultados import transformacao, resultados, plotar
from layout_calibragem import dados_reais, coef_intervalo, parametros_pso
import copy


def calibragem(selected, menu):
    if selected == menu[3]:
        st.markdown('#### Modelagem com os'
                    + ' :orange[coeficientes calibrados pelo algoritmo Particle Swarm Optimization (PSO)]:')


        paramentro = {'m_od': True, 'm_dbo': True, 'm_n': True, 'm_p': True,
                      'm_c': True, 'n_tb': 0, 's_t': True}
        lista_modelagem, data, labels, lista_tabs = inicio(paramentro)
        n_trib = lista_modelagem['n_tb']


        lista_parametros, list_name, list_valores, zona, hemisferio, dias = dados_iniciais(data, lista_modelagem, n_trib,
                                        labels, lista_tabs)
        
        list_name_salvo = copy.deepcopy(list_name)
        ponto_af = lista_parametros['p_af']
        ordem_desague = lista_parametros['l_des']

        lista_contr_retir = fun_contrib_retirad(data, n_trib, labels, lista_tabs, list_name, list_valores, lista_modelagem, dias)


        st.divider()
        st.markdown('''<div style='text-align: center;
            color: green;
            '>Dados gerais de TODAS as contribuições: </div>''',
            unsafe_allow_html=True)
        dados_reais(data, n_trib, labels, lista_tabs, list_name, list_valores, lista_modelagem, dias)

        coef_intervalo()

        parametros_pso()
        
        salvararquivo(lista_modelagem, lista_parametros, None, lista_contr_retir, list_name_salvo, list_valores)


        # botão
        botao = st.button(
            'Clique aqui para iniciar a modelagem',
            type='primary')

        if botao:
            list_tranfor = transformacao(lista_modelagem, lista_parametros, None,
                                        lista_contr_retir, list_name_salvo)
            
            lidt_df, list_entr, ordem_modelagem  = resultados(n_trib, list_tranfor, ponto_af, lista_modelagem, ordem_desague, dias)

            plotar(n_trib, lista_modelagem, lidt_df, list_entr, labels, zona, hemisferio, dias, ordem_modelagem)

            67
    return
