import streamlit as st
import copy
from funcoes.ferramentas import ordem_analise_sensibilidade, ajuste_trecho


reslt_calb = st.session_state.get('reslt_calb', 'ERRO')

if reslt_calb == 'ERRO':
    st.switch_page("pages/calibragem.py")



list_tranfor = copy.deepcopy(reslt_calb['list_tranfor_Geral'])

st.markdown('''<h3 style='text-align: center;
            color: teal;
            '>Análise de sensibilidade dos coeficientes do modelo </h3>''',
            unsafe_allow_html=True)

fixar_coef, seq_coef = ordem_analise_sensibilidade(list_tranfor, reslt_calb['ponto_af'],
                                         reslt_calb['lista_modelagem'], reslt_calb['ordem_desague'],
                                         reslt_calb['lista_hidraulica_ord'], reslt_calb['ordem_modelagem'])


botao_as = st.button('Calibrar esse conjunto', type='primary')


if botao_as:
    trecho_hidr = ajuste_trecho(list_tranfor, reslt_calb['lista_hidraulica_ord'], reslt_calb['list_ordem_coef'],
                                0, 0, reslt_calb['ordem_final'], reslt_calb['ordem_modelagem'])
    
    
    st.session_state['anotacoes'] = {'marcador_global': 0, 'marcador_global_interno': 0, 'trecho': trecho_hidr,
                                           'fixar': [fixar_coef, seq_coef], 'VarBolean': False, 'transf_final': copy.deepcopy(list_tranfor),
                                           'lista_coef_gerados': [], 'lista_apt_gerados': []}


    st.switch_page("pages/resultados_calib_pso.py")