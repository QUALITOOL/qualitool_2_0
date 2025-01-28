import streamlit as st
import copy
from funcoes.ferramentas import estrutura_calibracao, ajuste_trecho, tabelar
from funcoes.equacoes import salvando_conc

anotacoes = st.session_state.get('anotacoes', 'ERRO')
reslt_calb = st.session_state.get('reslt_calb', 'ERRO')


if reslt_calb == 'ERRO' or anotacoes == 'ERRO':
    st.switch_page("pages/calibragem.py")

marcador_conj_global = anotacoes['marcador_global']
marcador_conj_interno = anotacoes['marcador_global_interno']
fixar = anotacoes['fixar']
trecho_hidr = anotacoes['trecho']
var_bol = anotacoes['VarBolean']
transf_final = anotacoes['transf_final']
lista_coef_gerados = anotacoes['lista_coef_gerados']
lista_apt_gerados = anotacoes['lista_apt_gerados']

list_tranfor = copy.deepcopy(reslt_calb['list_tranfor_Geral'])


ordem_final = reslt_calb['ordem_final']
n_trib = reslt_calb['n_trib']
ponto_af = reslt_calb['ponto_af']
lista_modelagem = reslt_calb['lista_modelagem']
ordem_desague = reslt_calb['ordem_desague']
dias = reslt_calb['dias']
labels = reslt_calb['labels']
list_ordem_coef = reslt_calb['list_ordem_coef']
list_ordem_dr = reslt_calb['list_ordem_dr']
lista_hidr_model = reslt_calb['lista_hidraulica_ord']
ordem_modelagem = reslt_calb['ordem_modelagem']
ordem_final_coef = reslt_calb['ordem_final_coef']
lista_par_pos = reslt_calb['lista_par_pos']

text_lb = ''
atv = False
if len(ordem_final_coef[marcador_conj_global]) == 0:
    text_lb = labels[ordem_final[marcador_conj_global][-1]]
else:
    for ord in ordem_final_coef[marcador_conj_global][marcador_conj_interno]:
        if atv:
            text_lb += ' - '
        text_lb += labels[ord]
        atv = True
    text_lb += ' - ' + labels[ordem_final[marcador_conj_global][-1]]
st.markdown('''<h3 style='text-align: center;
            color: teal;
            '>Calibração dos coeficientes por PSO</h3>''',
            unsafe_allow_html=True)
st.markdown('''<h6 style='text-align: center;
            color: gray;
            '>Trecho(s): ''' + str(text_lb) + '. </h6>',
            unsafe_allow_html=True)
st.markdown('''<h5 style='text-align: center;
            color: gray;
            '>Coeficiente do ponto '''
            + str(list_ordem_coef[marcador_conj_global][marcador_conj_interno])
            + ' do ' + str(labels[ordem_final[marcador_conj_global][-1]]) + ':</h5>',
            unsafe_allow_html=True)


if var_bol:
    coef_ponto = tabelar(lista_modelagem)
else:
    
    coef_ponto, apt_ponto = estrutura_calibracao(list_tranfor, fixar[0], fixar[1], list_ordem_coef, list_ordem_dr,
                                      marcador_conj_global, marcador_conj_interno, ordem_final, lista_par_pos,
                                      ponto_af, lista_modelagem, lista_hidr_model, ordem_desague, trecho_hidr, dias)
    lista_coef_gerados.append(coef_ponto)
    lista_apt_gerados.append(apt_ponto)


esquerda, centro, direita = st.columns(3)

if var_bol == False:
    botao_rerodar = esquerda.button("Reiniciar busca neste trecho", use_container_width=True)

    if botao_rerodar:

        st.switch_page("pages/resultados_calib_pso.py")

    botao_tabelar = centro.button("Escolher valores tabelados", use_container_width=True)

    if botao_tabelar:
        
        st.session_state['anotacoes'] = {'marcador_global': marcador_conj_global, 'marcador_global_interno': marcador_conj_interno,
                                         'trecho': trecho_hidr, 'fixar': fixar, 'VarBolean': True, 'transf_final': transf_final}
        st.switch_page("pages/resultados_calib_pso.py")
else:
    voltar = esquerda.button("Voltar para busca", use_container_width=True)

    if voltar:
        st.session_state['anotacoes'] = {'marcador_global': marcador_conj_global, 'marcador_global_interno': marcador_conj_interno,
                                         'trecho': trecho_hidr, 'fixar': fixar, 'VarBolean': False, 'transf_final': transf_final}
        st.switch_page("pages/resultados_calib_pso.py")
botao_proximo = direita.button('Próximo trecho', type='primary', use_container_width=True)

if botao_proximo:
# Salvando os valores do coeficiente calibrado ou tabelado
    if len(lista_coef_gerados) > 0:
        coef_ponto = copy.deepcopy(lista_coef_gerados[lista_apt_gerados.index(min(lista_apt_gerados))])

    id_rio_calb = ordem_final[marcador_conj_global][-1]
    ordem_coef = list_ordem_coef[marcador_conj_global][marcador_conj_interno]
    transf_final[id_rio_calb].lista_e_coeficientes[ordem_coef].coeficientes = coef_ponto
    if len(ordem_final_coef[marcador_conj_global]) > 0:
        for rio_af_calb in ordem_final_coef[marcador_conj_global][marcador_conj_interno]:
            transf_final[rio_af_calb].lista_e_coeficientes[0].coeficientes = coef_ponto
            transf_final[rio_af_calb].lista_e_coeficientes[0].comprimento = 0.0

    # Salvando a concentração do último ponto calibrado ou tabelado
    list_tranfor = salvando_conc(list_tranfor, ordem_final, marcador_conj_global,
                                trecho_hidr, coef_ponto, lista_modelagem, lista_hidr_model, ordem_desague, ponto_af)
    
    if marcador_conj_interno == (len(list_ordem_coef[marcador_conj_global]) - 1):
        if marcador_conj_global == (len(list_ordem_coef) - 1):
            id_rio_calb = ordem_final[marcador_conj_global][-1]
            ordem_coef = list_ordem_coef[marcador_conj_global][marcador_conj_interno]
            transf_final[id_rio_calb].lista_e_coeficientes[ordem_coef].coeficientes = coef_ponto
            st.switch_page("pages/resultados_calib.py")

        else:
            marcador_conj_interno = 0
            marcador_conj_global += 1

    else:
        marcador_conj_interno += 1
    

    trecho_hidr = ajuste_trecho(list_tranfor, reslt_calb['lista_hidraulica_ord'], reslt_calb['list_ordem_coef'],
                                marcador_conj_global, marcador_conj_interno,
                                reslt_calb['ordem_final'], ordem_modelagem)

    st.session_state['anotacoes'] = {'marcador_global': marcador_conj_global, 'marcador_global_interno': marcador_conj_interno,
                                        'trecho': trecho_hidr, 'fixar': fixar, 'VarBolean': False, 'transf_final': transf_final}

    st.session_state['reslt_calb'] =  {'list_tranfor_Geral': list_tranfor, 'ordem_final': ordem_final,
                                'n_trib': n_trib, 'ponto_af': ponto_af, 'lista_modelagem': lista_modelagem,
                                'ordem_desague': ordem_desague, 'dias': dias, 'labels': labels,
                                'zona': reslt_calb['zona'], 'hemisferio': reslt_calb['hemisferio'], 'list_ordem_coef': list_ordem_coef,
                                'list_ordem_dr': list_ordem_dr, 'lista_hidraulica_ord': lista_hidr_model,
                                'ordem_modelagem': ordem_modelagem, 'ordem_final_coef': ordem_final_coef,
                                'lista_par_pos': lista_par_pos}
    

    st.switch_page("pages/resultados_calib_pso.py")
