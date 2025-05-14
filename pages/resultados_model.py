import streamlit as st
import pandas as pd
from funcoes.equacoes import modelagem_Final
from funcoes.ferramentas import plotar
import copy

reslt_model = st.session_state.get('reslt_model', "ERRO")

if reslt_model == [] or reslt_model == 'ERRO':
    st.switch_page("pages/modelagem.py")

n_tributarios = reslt_model[0]
list_tranfor = reslt_model[1]
ponto_af = reslt_model[2]
lista_modelagem = reslt_model[3]
ordem_desague = reslt_model[4]
dias = reslt_model[5]
labels = reslt_model[6]
zona = reslt_model[7]
hemisferio = reslt_model[8]

print('aqui2')
st.markdown('''<h3 style='text-align: center;
            color: black;
            '>Resultados </h3>''',
            unsafe_allow_html=True)

if n_tributarios > 0:
    ordem_modelagem = []
    ordem_da = copy.deepcopy(ordem_desague)
    ordem = list(range(1, len(ordem_da) + 1))
    while len(ordem) > 0:
        remov = []
        for ia in range(len(ordem)):
            if (ordem[ia] in ordem_da) == False:
                ordem_modelagem.append(ordem[ia])
                remov.append(ia)
        remov.reverse()
        for irem in remov:
            ordem.pop(irem)
            ordem_da.pop(irem)
    ordem_modelagem.append(0)
else:
    ordem_modelagem = [0]

lista_final, list_entr = modelagem_Final(list_tranfor, ponto_af,
                                         lista_modelagem,
                                         ordem_desague,
                                         ordem_modelagem)


lidt_df = []
for r in range(n_tributarios + 1):
    rio = lista_final[ordem_modelagem.index(r)]

    df = None
    obj_to_dict = {'rio': [],'latitude': [], 'longitude': [],
                   'altitude': [], 'comprimento': [], 'vazao': [],
                   'profundidade': [], 'velocidade': [],
                   'tensao_c': [], 'nivel_dagua': [],
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
    

    for idata in (range(len(rio[0].hidraulica.vazao))):
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


plotar(n_tributarios, lista_modelagem, lidt_df, list_entr, labels,
       zona, hemisferio, dias)

st.session_state['reslt_model'] = []