import streamlit as st
from funcoes.layout_modelagem import dados_iniciais, fun_contrib_retirad
from funcoes.layout_calibragem import inicio_calib, dados_reais, coef_intervalo
from funcoes.ferramentas import transformacao_calib, ordem_desague_geral, lista_hidraulica
import copy
import pandas as pd


st.markdown('#### Modelagem com os'
            + ' :orange[coeficientes calibrados pelo algoritmo PSO (Particle Swarm Optimization)]:')


paramentro = {'m_od': True, 'm_dbo': True, 'm_n': True, 'm_p': True,
                'm_c': True, 'n_tb': 0, 's_t': True}
lista_modelagem, data, labels, lista_tabs, lista_par_pos = inicio_calib(paramentro)
n_trib = lista_modelagem['n_tb']


lista_parametros, list_name, list_valores, zona, hemisferio, dias = dados_iniciais(data, lista_modelagem, n_trib,
                                labels, lista_tabs)

list_name_salvo = copy.deepcopy(list_name)
ponto_af = lista_parametros['p_af']
ordem_desague = lista_parametros['l_des']

lista_contr_retir = fun_contrib_retirad(data, n_trib, labels, lista_tabs, list_name, list_valores, lista_modelagem, dias)

dados_inter_coef = coef_intervalo(lista_modelagem, n_trib, labels, lista_tabs)

lista_dados_reais = dados_reais(n_trib, labels, lista_tabs, list_name, list_valores,
                                lista_modelagem, dados_inter_coef)


# botão
botao = st.button(
    'Clique aqui para iniciar a busca',
    type='primary')

if botao:

    list_tranfor_Geral = transformacao_calib(lista_modelagem, lista_parametros, dados_inter_coef,
                                lista_contr_retir, list_name_salvo, lista_dados_reais)
    
    
    ordem_modelagem, ordem_final, list_ordem_coef, list_ordem_dr, ordem_final_coef = ordem_desague_geral(ordem_desague, n_trib, dados_inter_coef,
                                                                          lista_dados_reais, list_tranfor_Geral, ponto_af)

    lista_hidraulica_ord = lista_hidraulica(list_tranfor_Geral, ordem_modelagem, ordem_desague, ponto_af)

    dias = pd.to_datetime(dias)

    st.session_state['reslt_calb'] =  {'list_tranfor_Geral': list_tranfor_Geral, 'ordem_final': ordem_final,
                                       'n_trib': n_trib, 'ponto_af': ponto_af, 'lista_modelagem': lista_modelagem,
                                       'ordem_desague': ordem_desague, 'dias': dias, 'labels': labels,
                                       'zona': zona, 'hemisferio': hemisferio, 'list_ordem_coef': list_ordem_coef,
                                       'list_ordem_dr': list_ordem_dr, 'lista_hidraulica_ord': lista_hidraulica_ord,
                                       'ordem_modelagem': ordem_modelagem, 'ordem_final_coef': ordem_final_coef,
                                       'lista_par_pos': lista_par_pos}

    st.switch_page("pages/resultados_calib_as.py")


