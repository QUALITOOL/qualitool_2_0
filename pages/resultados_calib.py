import streamlit as st
import pandas as pd
from funcoes.equacoes import modelagem_Final_2
from funcoes.ferramentas import plotar
import copy

reslt_calb = st.session_state.get('reslt_calb', 'ERRO')
anotacoes = st.session_state.get('anotacoes', 'ERRO')
reslt_calb = st.session_state.get('reslt_calb', 'ERRO')
fixar = anotacoes['fixar']
trecho_hidr = anotacoes['trecho']
var_bol = anotacoes['VarBolean']
transf_final = anotacoes['transf_final']


if reslt_calb == 'ERRO':
    st.switch_page("pages/calibragem.py")


st.markdown('''<h3 style='text-align: center;
            color: black;
            '>Resultados </h3>''',
            unsafe_allow_html=True)

container4 = st.container(border=True)
with container4:
    for cj_rio in range(len(reslt_calb['ordem_final_coef'])):
        for cj_cf in range(len(reslt_calb['list_ordem_coef'][cj_rio])):
            text_lb = ''
            atv = False
            if len(reslt_calb['ordem_final_coef'][cj_rio]) == 0:
                text_lb = reslt_calb['labels'][reslt_calb['ordem_final'][cj_rio][-1]]
            else:
                for ord in reslt_calb['ordem_final_coef'][cj_rio][cj_cf]:
                    if atv:
                        text_lb += ' - '
                    text_lb += reslt_calb['labels'][ord]
                    atv = True
                text_lb += ' - ' + reslt_calb['labels'][reslt_calb['ordem_final'][cj_rio][-1]]
            text_lb += ' (a partir do conjuntos de coeficientes do Ponto ' + str(reslt_calb['list_ordem_coef'][cj_rio][cj_cf]) + '):'
            st.markdown('- Para o(s) trechos(s): :orange[**' + text_lb + '**]')
            
            coef_final = transf_final[cj_rio].lista_e_coeficientes[cj_cf].coeficientes
            conj_cf_final = {}
            for tx in range(len(fixar[1])):
                conj_cf_final[fixar[1][tx]] = [getattr(coef_final, fixar[1][tx])]
            st.dataframe(copy.deepcopy(conj_cf_final))


lista_modelagem = reslt_calb['lista_modelagem']
n_tributarios = reslt_calb['n_trib']
dias = reslt_calb['dias']
ordem_modelagem = reslt_calb['ordem_modelagem']
labels = reslt_calb['labels']
zona = reslt_calb['zona']
hemisferio = reslt_calb['hemisferio']
lista_final, list_entr = modelagem_Final_2(transf_final, reslt_calb['ponto_af'], lista_modelagem,
                                            reslt_calb['ordem_desague'], ordem_modelagem, reslt_calb['lista_hidraulica_ord'])
            

    
lidt_df = []
for r in ordem_modelagem:
    rio = lista_final[r]
    df = None
    obj_to_dict = {'rio': [],'latitude': [], 'longitude': [], 'altitude': [], 'comprimento': [], 'vazao': [],
                    'profundidade': [], 'velocidade': [], 'tensao_c': [], 'nivel_dagua': [],
                    'froude': []}
    if lista_modelagem['s_t']:
        dt = {'data': []}
        dt.update(obj_to_dict)
        obj_to_dict = dt
    if lista_modelagem['m_od']:
        obj_to_dict['conc_od'] = []
        obj_to_dict['conc_dbo'] = []
    if lista_modelagem['m_n']:
        obj_to_dict['conc_no'] = []
        obj_to_dict['conc_n_amon'] = []
        obj_to_dict['conc_nitrito'] = []
        obj_to_dict['conc_nitrato'] = []
    if lista_modelagem['m_p']:
        obj_to_dict['conc_p_org'] = []
        obj_to_dict['conc_p_inorg'] = []
        obj_to_dict['conc_p_total'] = []
    if lista_modelagem['m_c']:
        obj_to_dict['conc_e_coli'] = []
    
    for idata in (range(len(rio[r].hidraulica.vazao))):
        for i in range(len(rio)):
            h = rio[i].hidraulica
            cc = rio[i].concentracoes
            
            obj_to_dict['rio'].append(rio[i].rio)
            obj_to_dict['latitude'].append(h.latitude)
            obj_to_dict['longitude'].append(h.longitude)
            obj_to_dict['altitude'].append(h.altitude)
            obj_to_dict['comprimento'].append(h.comprimento)
            obj_to_dict['vazao'].append(h.vazao[idata])
            obj_to_dict['profundidade'].append(h.profundidade[idata])
            obj_to_dict['velocidade'].append(h.velocidade[idata])
            obj_to_dict['tensao_c'].append(h.tensao_c[idata])
            obj_to_dict['nivel_dagua'].append(h.nivel_dagua[idata])
            obj_to_dict['froude'].append(h.froude[idata])

            if lista_modelagem['s_t']:
                obj_to_dict['data'].append(dias[idata])
            if lista_modelagem['m_od']:
                obj_to_dict['conc_od'].append(cc.conc_od[idata])
                obj_to_dict['conc_dbo'].append(cc.conc_dbo[idata])
            if lista_modelagem['m_n']:
                obj_to_dict['conc_no'].append(cc.conc_no[idata])
                obj_to_dict['conc_n_amon'].append(cc.conc_n_amon[idata])
                obj_to_dict['conc_nitrito'].append(cc.conc_nitrito[idata])
                obj_to_dict['conc_nitrato'].append(cc.conc_nitrato[idata])
            if lista_modelagem['m_p']:
                obj_to_dict['conc_p_org'].append(cc.conc_p_org[idata])
                obj_to_dict['conc_p_inorg'].append(cc.conc_p_inorg[idata])
                obj_to_dict['conc_p_total'].append(cc.conc_p_total[idata])
            if lista_modelagem['m_c']:
                obj_to_dict['conc_e_coli'].append(cc.conc_e_coli[idata])

    df = pd.DataFrame(obj_to_dict)
    lidt_df.append(df)

# return lidt_df, list_entr, ordem_modelagem
plotar(n_tributarios, lista_modelagem, lidt_df, list_entr, labels, zona, hemisferio, dias, ordem_modelagem)
# return