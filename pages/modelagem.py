import streamlit as st
from funcoes.layout_modelagem import inicio, dados_iniciais
from funcoes.layout_modelagem import fun_contrib_retirad
from funcoes.layout_modelagem import coeficientes, salvararquivo
from funcoes.ferramentas import transformacao
import copy


st.markdown('#### Modelagem com os'
            + ' :orange[coeficientes predefinidos]:')

paramentro = {'m_od': True, 'm_dbo': True, 'm_n': True,
              'm_p': True, 'm_c': True, 'n_tb': 0, 's_t': True}
lista_modelagem, data, labels, lista_tabs = inicio(paramentro)
n_trib = lista_modelagem['n_tb']


lista_parametros, list_name, list_valores, zona, hemisferio, dias = dados_iniciais(data, lista_modelagem, n_trib,
                                labels, lista_tabs)

list_name_salvo = copy.deepcopy(list_name)
ponto_af = lista_parametros['p_af']
ordem_desague = lista_parametros['l_des']

lista_contr_retir = fun_contrib_retirad(data, n_trib, labels, lista_tabs,
                                        list_name, list_valores, lista_modelagem, dias)

lista_coeficientes = coeficientes(data, lista_modelagem, n_trib,
                                labels, lista_tabs, dias)


salvararquivo(lista_modelagem, lista_parametros, lista_coeficientes, lista_contr_retir, list_name_salvo, list_valores)


# botão
botao = st.button(
    'Clique aqui para iniciar a modelagem',
    type='primary')



if botao:

    list_tranfor = transformacao(lista_modelagem, lista_parametros,
                                 lista_coeficientes,
                                 lista_contr_retir, list_name_salvo)
    

    st.session_state['reslt_model'] = [n_trib, list_tranfor,
                                       ponto_af, lista_modelagem,
                                       ordem_desague, dias, labels,
                                       zona, hemisferio]

    st.switch_page("pages/resultados_model.py")


