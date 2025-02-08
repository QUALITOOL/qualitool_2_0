import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from funcoes.equacoes import lista_hidr, menor_dist, modelagem_as_final, func_hidraulica, menor_dist2, ajust_porc, modelagem_calib_final
import copy
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from funcoes.otimizador import gera_enxame_inicial, dict_obtj, melhores_resultados, pso
from functools import partial
from plotly.subplots import make_subplots
import random
import altair as alt

# OBJETOS
# Secções Tranversais
class SeccaoTransversal:
    def __init__(self, lat, long, comp, l_rio, ang_esq, rug, ang_dir):
        self.latitude = lat
        self.longitude = long
        self.comprimento = comp
        self.largura_rio = l_rio
        self.ang_esquerdo = ang_esq
        self.rugosidade_n = rug
        self.ang_direito = ang_dir


# Hidráulica
class Hidraulica:
    def __init__(self, lat, long, comp, vazao, rug, l_rio, altitude, inclinacao, ang_esq,
                 ang_dir, prof, veloc, to, nivel_ag, froude):
        self.latitude = lat
        self.longitude = long
        self.comprimento = comp
        self.vazao = vazao
        self.rugosidade_n = rug
        self.largura_rio = l_rio
        self.altitude = altitude
        self.inclinacao = inclinacao
        self.ang_esquerdo = ang_esq
        self.ang_direito = ang_dir
        self.profundidade = prof
        self.velocidade = veloc
        self.tensao_c = to
        self.nivel_dagua = nivel_ag 


# Coeficientes
class CoeficientesEntrada:
    def __init__(self, lat, long, comp, coeficientes, rio):
        self.latitude = lat
        self.longitude = long
        self.comprimento = comp
        self.coeficientes = coeficientes
        self.rio = rio
                 
class Coeficientes:
    def __init__(self, temperatura, k_2_calculavel, k_2_max, k_2, k_1, s_d, k_d, k_s, l_rd, k_so,
                 k_oa, k_an, k_nn, s_amon, k_spo, k_oi, k_b, r_o2_amon, k_nit_od, s_pinorg):
        self.temperatura = temperatura
        self.k_2_calculavel = k_2_calculavel
        self.k_2_max = k_2_max
        self.k_2 = k_2
        self.k_1 = k_1
        self.s_d = s_d
        self.k_d = k_d
        self.k_s = k_s
        self.l_rd = l_rd
        self.k_so = k_so
        self.k_oa = k_oa
        self.k_an = k_an
        self.k_nn = k_nn
        self.s_amon = s_amon
        self.k_spo = k_spo
        self.k_oi = k_oi
        self.k_b = k_b
        self.r_o2_amon = r_o2_amon
        self.k_nit_od = k_nit_od
        self.s_pinorg = s_pinorg


# Concentrações
class Concentracoes:
    def __init__(self, od, dbo, no, n_amon, nitrato, nitrito, p_org, p_inorg, p_total, e_coli):
        self.conc_od = od
        self.conc_dbo = dbo
        self.conc_no = no
        self.conc_n_amon = n_amon
        self.conc_nitrato = nitrato
        self.conc_nitrito = nitrito
        self.conc_p_org = p_org
        self.conc_p_inorg = p_inorg
        self.conc_p_total = p_total
        self.conc_e_coli = e_coli


# Dados reais
class DadosReais:
    def __init__(self, lat, long, comp, c_gerais, data_dr, vazao, descricao, rio):
        self.latitude = lat
        self.longitude = long
        self.comprimento = comp
        self.concentracoes = c_gerais
        self.data_dr = data_dr
        self.vazao = vazao
        self.descricao = descricao
        self.rio = rio

# Saídas Pontuais
class SaidaPontual:
    def __init__(self, lat, long, comp, vazao, descricao, rio):
        self.latitude = lat
        self.longitude = long
        self.comprimento = comp
        self.vazao = vazao
        self.descricao = descricao
        self.rio = rio



# Entradas Pontuais
class EntradaPontual:
    def __init__(self, lat, long, comp, c_gerais, vazao, descricao, rio):
        self.latitude = lat
        self.longitude = long
        self.comprimento = comp
        self.concentracoes = c_gerais
        self.vazao = vazao
        self.descricao = descricao
        self.rio = rio


# Entradas Difusas
class EntradaDifusa:
    def __init__(self, lat_i, long_i, lat_f, long_f, comp_i, comp_f, c_gerais, vazao, descricao, rio):
        self.latitude_inicial = lat_i
        self.longitude_inicial = long_i
        self.comprimento_inicial = comp_i
        self.latitude_final = lat_f
        self.longitude_final = long_f
        self.comprimento_final = comp_f
        self.concentracoes = c_gerais
        self.descricao = descricao
        self.vazao = vazao
        self.rio = rio


# Resultados finais
class Quanti_Qualitativo:
    def __init__(self, hidraulica, concentracoes, coeficientes, rio):
        self.hidraulica = hidraulica
        self.concentracoes = concentracoes
        self.coeficientes = coeficientes
        self.rio = rio


# Classe Geral
class Geral:
    def __init__(self, s_transversal, e_coeficientes, s_pontual, e_pontual,
                 e_difusa, hidraulica, rio, discretizacao):
        self.lista_s_transversal = s_transversal
        self.lista_e_coeficientes = e_coeficientes
        self.lista_s_pontual = s_pontual
        self.lista_e_pontual = e_pontual
        self.lista_e_difusa = e_difusa
        self.lista_hidraulica = hidraulica
        self.rio = rio
        self.discretizacao = discretizacao    


# Classe Geral Calib
class GeralCalib:
    def __init__(self, s_transversal, e_coeficientes, s_pontual, e_pontual,
                 e_difusa, dados_reais, hidraulica, rio, discretizacao):
        self.lista_s_transversal = s_transversal
        self.lista_e_coeficientes = e_coeficientes
        self.lista_s_pontual = s_pontual
        self.lista_e_pontual = e_pontual
        self.lista_e_difusa = e_difusa
        self.lista_dados_reais = dados_reais
        self.lista_hidraulica = hidraulica
        self.rio = rio
        self.discretizacao = discretizacao  


def transformacao(lista_modelagem, lista_parametros, lista_coeficiente,
                  lista_contr_retir, list_name):
    
    list_tranfor = []
    

    for i in range(lista_modelagem['n_tb'] + 1):
        hidraulica = (lista_hidr(lista_parametros['l_lo'][i],
                                 lista_parametros['l_la'][i],
                                 lista_parametros['l_a'][i],
                                 lista_parametros['l_c'][i],
                                 lista_parametros['l_d'][i]))
        
        lat_dis = []
        long_dis = []
        comp_dis = []
        for llc in range(len(hidraulica)):
            lat_dis.append(hidraulica[llc].latitude)
            long_dis.append(hidraulica[llc].longitude)
            comp_dis.append(hidraulica[llc].comprimento)


        coeficiente = []
        for k in range(lista_coeficiente['l_n_p'][i] + 1):
            k2_calc = False if lista_modelagem['é_calc'] else True
            
            coef = Coeficientes(np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('Temperatura (°C)')]),
                                k2_calc, 0, 0, 0,
                                0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0)

            if lista_modelagem['é_calc']:
                coef.k_2 = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('k2 (1/d)')])
            if lista_modelagem['é_calc'] == False and lista_modelagem['m_od'] == True:
                coef.k_2_max = lista_coeficiente['l_coe'][i + 1][k][0][3]
            if lista_modelagem['m_od']:
                coef.k_1 = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('k1 (1/d)')])
                coef.k_d = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('kd (1/d)')])
                coef.k_s = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('ks (1/d)')])
                coef.l_rd = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('lrd (gDBO5/m.d)')])
                coef.s_d = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('sd (1/d)')])
            if lista_modelagem['m_od'] == True and lista_modelagem['m_n'] == True:
                coef.r_o2_amon = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('O2namon (mgO2/mgNamon oxid)')])
            if lista_modelagem['m_n']:
                coef.k_oa = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('koa (1/d)')])
                coef.k_so = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('kso (1/d)')])
                coef.k_an = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('kan (1/d)')])
                coef.s_amon = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('Snamon (g/m2.d)')])
                coef.k_nn = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('knn (1/d)')])
                coef.k_nit_od = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('knitr (1/d)')])
            if lista_modelagem['m_p']:
                coef.k_oi = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('koi (1/d)')])
                coef.k_spo = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('kspo (1/d)')])
                coef.s_pinorg = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('spinorg (1/d)')])
            if lista_modelagem['m_c']:
                coef.k_b = np.array(lista_coeficiente['l_coe'][i + 1][k][1][lista_coeficiente['l_coe'][0].index('kb (1/d)')])

            comp_C = menor_dist(lat_dis, long_dis,
                                comp_dis, lista_coeficiente['l_coe'][i + 1][k][0][0],
                                lista_coeficiente['l_coe'][i + 1][k][0][1], lista_coeficiente['l_coe'][i + 1][k][0][2])

            coeficiente.append(copy.deepcopy(CoeficientesEntrada(lista_coeficiente['l_coe'][i + 1][k][0][0],
                                                                 lista_coeficiente['l_coe'][i + 1][k][0][1],
                                                                 comp_C,
                                                                 copy.deepcopy(coef),
                                                                 i)))
    
        
        geometria = []
        for j in range(lista_parametros['l_q_s'][i] + 1):
            comp_g = menor_dist(lat_dis, long_dis,
                                comp_dis, lista_parametros['l_sc'][i][j][0],
                                lista_parametros['l_sc'][i][j][1], lista_parametros['l_sc'][i][j][2])
            
            geometria.append(copy.deepcopy(SeccaoTransversal(lista_parametros['l_sc'][i][j][0],
                                                             lista_parametros['l_sc'][i][j][1],
                                                             comp_g,
                                                             lista_parametros['l_sc'][i][j][4],
                                                             lista_parametros['l_sc'][i][j][5],
                                                             lista_parametros['l_sc'][i][j][3],
                                                             lista_parametros['l_sc'][i][j][6])))
        

        
        conc = Concentracoes([0], [0], [0], [0], [0],
                             [0], [0], [0], [0], [0])
        # Entradas Pontuais
        if lista_modelagem['m_od']:
            id_od = list_name.index('OD (mg/L)')
            conc.conc_od = np.array(lista_parametros['l_v_i'][i][id_od])
            id_dbo = list_name.index('DBO (mg/L)')
            conc.conc_dbo = np.array(lista_parametros['l_v_i'][i][id_dbo])
        if lista_modelagem['m_n']:
            id_no = list_name.index('N-org (mg/L)')
            conc.conc_no = np.array(lista_parametros['l_v_i'][i][id_no])
            id_n_amon = list_name.index('N-amon (mg/L)')
            conc.conc_n_amon = np.array(lista_parametros['l_v_i'][i][id_n_amon])
            id_nitrito = list_name.index('N-nitri (mg/L)')
            conc.conc_nitrito = np.array(lista_parametros['l_v_i'][i][id_nitrito])
            id_nitrato = list_name.index('N-nitra (mg/L)')
            conc.conc_nitrato = np.array(lista_parametros['l_v_i'][i][id_nitrato])
        if lista_modelagem['m_p']:
            id_p_org = list_name.index('P-org (mg/L)')
            conc.conc_p_org = np.array(lista_parametros['l_v_i'][i][id_p_org])
            id_p_inorg = list_name.index('P-inorg (mg/L)')
            conc.conc_p_inorg = np.array(lista_parametros['l_v_i'][i][id_p_inorg])
            conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
        if lista_modelagem['m_c']:
            id_e_coli = list_name.index('E-coli (NMP/100ml)')
            conc.conc_e_coli = np.array(lista_parametros['l_v_i'][i][id_e_coli])

        id = 1 if lista_modelagem['s_t'] else 0
        id_q = id
                
        conc_ep = [copy.deepcopy(EntradaPontual(lista_parametros['l_la'][i][0],
                                                lista_parametros['l_lo'][i][0],
                                                0.0,
                                                copy.deepcopy(conc),
                                                np.array(lista_parametros['l_v_i'][i][id_q]),
                                                'Início',
                                                i))]
        
        id_q = 0
        # Entradas Pontuais
        if lista_contr_retir['l_q'][i][4]:

            for p in range(lista_contr_retir['l_q'][i][1]):

                if lista_modelagem['m_od']:
                    conc.conc_od = np.array(lista_contr_retir['l_ep'][i][p][1][id_od - id])
                    conc.conc_dbo = np.array(lista_contr_retir['l_ep'][i][p][1][id_dbo - id])
                if lista_modelagem['m_n']:
                    conc.conc_no = np.array(lista_contr_retir['l_ep'][i][p][1][id_no - id])
                    conc.conc_n_amon = np.array(lista_contr_retir['l_ep'][i][p][1][id_n_amon - id])
                    conc.conc_nitrito = np.array(lista_contr_retir['l_ep'][i][p][1][id_nitrito - id])
                    conc.conc_nitrato = np.array(lista_contr_retir['l_ep'][i][p][1][id_nitrato - id])
                if lista_modelagem['m_p']:
                    conc.conc_p_org = np.array(lista_contr_retir['l_ep'][i][p][1][id_p_org - id])
                    conc.conc_p_inorg = np.array(lista_contr_retir['l_ep'][i][p][1][id_p_inorg - id])
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem['m_c']:
                    conc.conc_e_coli = np.array(lista_contr_retir['l_ep'][i][p][1][id_e_coli - id])

                comp_ep = menor_dist(lat_dis, long_dis,
                                     comp_dis, lista_contr_retir['l_ep'][i][p][0][1],
                                     lista_contr_retir['l_ep'][i][p][0][2], lista_contr_retir['l_ep'][i][p][0][3])
                
                conc_ep.append(copy.deepcopy(EntradaPontual(lista_contr_retir['l_ep'][i][p][0][1],
                                                            lista_contr_retir['l_ep'][i][p][0][2],
                                                            comp_ep,
                                                            copy.deepcopy(conc),
                                                            np.array(lista_contr_retir['l_ep'][i][p][1][id_q]),
                                                            lista_contr_retir['l_ep'][i][p][0][0],
                                                            i)))

        # Entradas Difusas
        conc_ed = []
        if lista_contr_retir['l_q'][i][5]:
            for d in range(lista_contr_retir['l_q'][i][2]):
                
                if lista_modelagem['m_od']:
                    conc.conc_od = np.array(lista_contr_retir['l_ed'][i][d][1][id_od - id])
                    conc.conc_dbo = np.array(lista_contr_retir['l_ed'][i][d][1][id_dbo - id])
                if lista_modelagem['m_n']:
                    conc.conc_no = np.array(lista_contr_retir['l_ed'][i][d][1][id_no - id])
                    conc.conc_n_amon = np.array(lista_contr_retir['l_ed'][i][d][1][id_n_amon - id])
                    conc.conc_nitrito = np.array(lista_contr_retir['l_ed'][i][d][1][id_nitrito - id])
                    conc.conc_nitrato = np.array(lista_contr_retir['l_ed'][i][d][1][id_nitrato - id])
                if lista_modelagem['m_p']:
                    conc.conc_p_org = np.array(lista_contr_retir['l_ed'][i][d][1][id_p_org - id])
                    conc.conc_p_inorg = np.array(lista_contr_retir['l_ed'][i][d][1][id_p_inorg - id])
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem['m_c']:
                    conc.conc_e_coli = np.array(lista_contr_retir['l_ed'][i][d][1][id_e_coli - id])


                comp_ed_i = menor_dist(lat_dis, long_dis,
                                       comp_dis, lista_contr_retir['l_ed'][i][d][0][1],
                                       lista_contr_retir['l_ed'][i][d][0][3], lista_contr_retir['l_ed'][i][d][0][5])
                comp_ed_f = menor_dist(lat_dis, long_dis,
                                       comp_dis, lista_contr_retir['l_ed'][i][d][0][2],
                                       lista_contr_retir['l_ed'][i][d][0][4], lista_contr_retir['l_ed'][i][d][0][6])

                conc_ed.append(copy.deepcopy(EntradaDifusa(lista_contr_retir['l_ed'][i][d][0][1],
                                                            lista_contr_retir['l_ed'][i][d][0][3],
                                                            lista_contr_retir['l_ed'][i][d][0][2],
                                                            lista_contr_retir['l_ed'][i][d][0][4],
                                                            comp_ed_i,
                                                            comp_ed_f,
                                                            copy.deepcopy(conc),
                                                            np.array(lista_contr_retir['l_ed'][i][d][1][id_q]),
                                                            lista_contr_retir['l_ed'][i][d][0][0],
                                                            i)))


        # Saídas Pontuais
        conc_r = []
        if lista_contr_retir['l_q'][i][3]:
            for r in range(lista_contr_retir['l_q'][i][0]):
                
                comp_r = menor_dist(lat_dis, long_dis,
                                    comp_dis, lista_contr_retir['l_r'][i][r][0][1],
                                    lista_contr_retir['l_r'][i][r][0][2], lista_contr_retir['l_r'][i][r][0][3])

                conc_r.append(copy.deepcopy(SaidaPontual(lista_contr_retir['l_r'][i][r][0][1],
                                                         lista_contr_retir['l_r'][i][r][0][2],
                                                         comp_r,
                                                         np.array(lista_contr_retir['l_r'][i][r][1][id_q]),
                                                         lista_contr_retir['l_r'][i][r][0][0],
                                                         i)))

        list_tranfor.append(copy.deepcopy(Geral(geometria,
                                                coeficiente,
                                                conc_r,
                                                conc_ep,
                                                conc_ed,
                                                hidraulica,
                                                i,
                                                lista_parametros['l_d'][i])))

    return list_tranfor


def plot_map(maps, df_new, colun, title, inverse_b):
    
    maps.add_trace(
        go.Scattermapbox(lon=df_new['lon'], lat=df_new['lat'], name=title,
                        marker={"autocolorscale": False,
                                "showscale":True, "size": 6, "opacity": 0.8,
                                "color": colun, "colorscale": 'haline',
                                "colorbar": dict(orientation='h')},
                        marker_reversescale=inverse_b))
    
    return


def plotar(n_tributarios, lista_modelagem, lidt_df, list_entr, labels, zona, hemisferio, dias):

    list_tab = ['Gráficos do Rio Principal', 'Tabelas']
    str_lat = str(lidt_df[0]['latitude'][0])
    if str_lat != 'nan' and str_lat != 'None':
        list_tab.append('Representações geoespaciais')

    result_tabs = st.tabs(list_tab)

    with result_tabs[0]:
        if lista_modelagem['s_t']:
            df = lidt_df[0].loc[lidt_df[0]['data'] == dias[-1]]
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(title_text="Concentrações do dia " + str(dias[-1].date()),
                                title_font_color="teal")

        else:
            df = lidt_df[0]
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(title_text="Concentrações",
                                title_font_color="teal")

        if lista_modelagem['m_od']:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_od"],
                                mode='lines',
                                name='OD'))
        
        if lista_modelagem['m_od']:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_dbo"],
                                mode='lines',
                                name='DBO'))
        
        if lista_modelagem['m_n']:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_no"],
                                mode='lines',
                                name='N-org'))
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_n_amon"],
                                mode='lines',
                                name='N-amon'))
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_nitrato"],
                                mode='lines',
                                name='N-nitri'))
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_nitrito"],
                                mode='lines',
                                name='N-nitra'))
        if lista_modelagem['m_p']:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_p_org"],
                                mode='lines',
                                name='P-org'))
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_p_inorg"],
                                mode='lines',
                                name='P-inorg'))
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_p_total"],
                                mode='lines',
                                name='P total'))
        if lista_modelagem['m_c']:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_e_coli"],
                                mode='lines',
                                name='E-coli', yaxis="y2"))
            
        fig.update_xaxes(minor=dict(ticklen=3, tickcolor="black"))
        fig.update_yaxes(minor=dict(ticklen=3, tickcolor="black"))
        fig.update_layout(
            legend=dict(orientation="h",
                        yanchor="bottom",
                        y=1,
                        xanchor="right",
                        x=0.95),
            xaxis=dict(title="Comprimento (m)",
                        ticklen=4,
                        tickcolor="black",
                        showgrid=True,
                        showline=True),
            yaxis=dict(title="OD, DBO, N ou P (mg/L)",
                        showline=True,
                        tickcolor="black",
                        ticklen=4,
            ),
            yaxis2=dict(title="E-coli (NMP/100ml)",
                        overlaying="y",
                        side="right",
                        showline=True,
                        tickcolor="black",
                        ticklen=4
            ),)

        for pt in range(len(list_entr) - 1):
            if str(list_entr[pt + 1].descricao) == 'nan'or str(list_entr[pt + 1].descricao) == 'None':

                fig.add_vline(
                    x=list_entr[pt + 1].comprimento,
                    line_width=2,
                    line_dash="dot",
                    line_color="LightSeaGreen",
                    )
            else:
                fig.add_vline(
                    x=list_entr[pt + 1].comprimento,
                    line_width=2,
                    line_dash="dot",
                    line_color="LightSeaGreen",
                    annotation_text=int(list_entr[pt + 1].descricao),
                    annotation_position="top left",
                    )


        
        # Plot!
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.update_layout(title_text="Hidráulica",
                            title_font_color="teal")

        fig2.add_trace(go.Scatter(x=df["comprimento"], y=df["altitude"],
                            mode='lines',
                            name='Fundo do canal'))
        fig2.add_trace(go.Scatter(x=df["comprimento"], y=df["nivel_dagua"],
                            mode='lines',
                            name='Superfície livre'))
        fig2.add_trace(go.Scatter(x=df["comprimento"], y=df["vazao"],
                            mode='lines',
                            name='Vazão', yaxis="y2"))

        fig2.update_xaxes(minor=dict(ticklen=3, tickcolor="black"))
        fig2.update_yaxes(minor=dict(ticklen=3, tickcolor="black"))
        fig2.update_layout(
            legend=dict(orientation="h",
                        yanchor="bottom",
                        y=1,
                        xanchor="right",
                        x=0.5),
            xaxis=dict(title="Comprimento (m)",
                        ticklen=4,
                        tickcolor="black",
                        showgrid=True,
                        showline=True),
            yaxis=dict(title="Cota (m)",
                        showline=True,
                        tickcolor="black",
                        ticklen=4,
            ),
            yaxis2=dict(title="Vazão (m³/s)",
                        overlaying="y",
                        side="right",
                        showline=True,
                        tickcolor="black",
                        ticklen=4,
            ),)
        
        for pt in range(len(list_entr) - 1):

            if str(list_entr[pt + 1].descricao) == 'nan' or str(list_entr[pt + 1].descricao) == 'None':

                fig2.add_vline(
                    x=list_entr[pt + 1].comprimento,
                    line_width=2,
                    line_dash="dot",
                    line_color="LightSeaGreen",
                    )
            else:
                fig2.add_vline(
                    x=list_entr[pt + 1].comprimento,
                    line_width=2,
                    line_dash="dot",
                    line_color="LightSeaGreen",
                    annotation_text=int(list_entr[pt + 1].descricao),
                    annotation_position="top left",
                    )

        st.plotly_chart(fig2, use_container_width=True)

    with result_tabs[1]:
        for r1 in range(n_tributarios + 1):
            ex = st.expander('Resultados do ' + labels[r1])
            ex.write(lidt_df[r1])

        df_new = pd.concat(lidt_df)
        if len(lidt_df) > 1:
            ex2 = st.expander('Resultados Agrupado')
            ex2.write(df_new)

    if str_lat != 'nan' and str_lat != 'None':
        with result_tabs[2]:       

            from pyproj import Proj
            
            if lista_modelagem['s_t']:
                df_new = df_new.loc[df_new['data'] == dias[-1]]
                titulo = 'Concentrações do dia ' + str(dias[-1])
            else:
                titulo = 'Concentrações'

            myProj = Proj('+proj=utm +zone=' + str(zona)
                        + ' +' + str(hemisferio) + ' +ellps=WGS84',
                        preserve_units=False)
            df_new['lon'], df_new['lat'] = myProj(df_new['longitude'].values,
                                                  df_new['latitude'].values,
                                                  inverse=True)
            
            
            maps = go.Figure()

            maps.update_layout(title_text=titulo, title_font_color="teal",
                                    mapbox=dict(style='carto-positron',
                                                center=dict(lat=df_new["lat"].mean(),
                                                            lon=df_new["lon"].mean()),
                                                            zoom=10),
                                    legend_itemclick="toggleothers",
                                    margin={"r":0,"t":0,"l":0,"b":0})


            if lista_modelagem['m_od']:
                plot_map(maps, df_new, df_new["conc_od"], 'OD (mg/L)', False)               
            if lista_modelagem['m_dbo']:
                plot_map(maps, df_new, df_new["conc_dbo"], 'DBO (mg/L)', True)
            if lista_modelagem['m_p']:
                plot_map(maps, df_new, df_new["conc_p_org"], 'P-org (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_p_inorg"], 'P-inorg (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_p_total"], 'P total (mg/L)', True)     
            if lista_modelagem['m_n']:
                plot_map(maps, df_new, df_new["conc_no"], 'N-org (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_n_amon"], 'N-amon (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_nitrato"], 'N-nitri (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_nitrito"], 'N-nitra (mg/L)', True)
            if lista_modelagem['m_c']:
                plot_map(maps, df_new, df_new["conc_e_coli"], 'E-coli (NMP/100ml)', True)
            st.plotly_chart(maps, use_container_width=True)
    
    return



def transformacao_calib(lista_modelagem, lista_parametros, lista_coeficiente,
                  lista_contr_retir, list_name, lista_dados_reais):
    
    list_tranfor = []
    marcador_calib = 0
    

    for i in range(lista_modelagem['n_tb'] + 1):

        hidraulica = (lista_hidr(lista_parametros['l_lo'][i],
                                 lista_parametros['l_la'][i],
                                 lista_parametros['l_a'][i],
                                 lista_parametros['l_c'][i],
                                 lista_parametros['l_d'][i]))
        
        lat_dis = []
        long_dis = []
        comp_dis = []
        for llc in range(len(hidraulica)):
            lat_dis.append(hidraulica[llc].latitude)
            long_dis.append(hidraulica[llc].longitude)
            comp_dis.append(hidraulica[llc].comprimento)


        coeficiente = []
        if lista_coeficiente['calb_trib'][i]:
            for k in range(lista_coeficiente['l_n_p'][i] + 1):
                coef_Minimo = lista_coeficiente['l_coe'][i + 1][1][0]
                coef_Maximo = lista_coeficiente['l_coe'][i + 1][1][1]
                nomes_coef_int = lista_coeficiente['l_coe'][0]
                coef = Coeficientes([coef_Minimo[nomes_coef_int.index('Temperatura (°C)')],
                                    coef_Maximo[nomes_coef_int.index('Temperatura (°C)')]],
                                    False, 0, 0, 0,
                                    0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0)

                if lista_modelagem['m_od']:
                    coef.k_2 = [coef_Minimo[nomes_coef_int.index('k2 (1/d)')], coef_Maximo[nomes_coef_int.index('k2 (1/d)')]]
                    coef.k_1 = [coef_Minimo[nomes_coef_int.index('k1 (1/d)')], coef_Maximo[nomes_coef_int.index('k1 (1/d)')]]
                    coef.k_d = [coef_Minimo[nomes_coef_int.index('kd (1/d)')], coef_Maximo[nomes_coef_int.index('kd (1/d)')]]
                    coef.k_s = [coef_Minimo[nomes_coef_int.index('ks (1/d)')], coef_Maximo[nomes_coef_int.index('ks (1/d)')]]
                    coef.l_rd = [coef_Minimo[nomes_coef_int.index('lrd (gDBO5/m.d)')], coef_Maximo[nomes_coef_int.index('lrd (gDBO5/m.d)')]]
                    coef.s_d = [coef_Minimo[nomes_coef_int.index('sd (1/d)')], coef_Maximo[nomes_coef_int.index('sd (1/d)')]]

                if lista_modelagem['m_od'] == True and lista_modelagem['m_n'] == True:
                    coef.r_o2_amon = [coef_Minimo[nomes_coef_int.index('O2namon (mgO2/mgNamon oxid)')], coef_Maximo[nomes_coef_int.index('O2namon (mgO2/mgNamon oxid)')]]
                if lista_modelagem['m_n']:
                    coef.k_oa = [coef_Minimo[nomes_coef_int.index('koa (1/d)')], coef_Maximo[nomes_coef_int.index('koa (1/d)')]]
                    coef.k_so = [coef_Minimo[nomes_coef_int.index('kso (1/d)')], coef_Maximo[nomes_coef_int.index('kso (1/d)')]]
                    coef.k_an = [coef_Minimo[nomes_coef_int.index('kan (1/d)')], coef_Maximo[nomes_coef_int.index('kan (1/d)')]]
                    coef.s_amon = [coef_Minimo[nomes_coef_int.index('Snamon (g/m2.d)')], coef_Maximo[nomes_coef_int.index('Snamon (g/m2.d)')]]
                    coef.k_nn = [coef_Minimo[nomes_coef_int.index('knn (1/d)')], coef_Maximo[nomes_coef_int.index('knn (1/d)')]]
                    coef.k_nit_od = [coef_Minimo[nomes_coef_int.index('knitr (1/d)')], coef_Maximo[nomes_coef_int.index('knitr (1/d)')]]
                if lista_modelagem['m_p']:
                    coef.k_oi = [coef_Minimo[nomes_coef_int.index('koi (1/d)')], coef_Maximo[nomes_coef_int.index('koi (1/d)')]]
                    coef.k_spo = [coef_Minimo[nomes_coef_int.index('kspo (1/d)')], coef_Maximo[nomes_coef_int.index('kspo (1/d)')]]
                    coef.s_pinorg = [coef_Minimo[nomes_coef_int.index('spinorg (1/d)')], coef_Maximo[nomes_coef_int.index('spinorg (1/d)')]]
                if lista_modelagem['m_c']:
                    coef.k_b = [coef_Minimo[nomes_coef_int.index('kb (1/d)')], coef_Maximo[nomes_coef_int.index('kb (1/d)')]]

                comp_C = menor_dist(lat_dis, long_dis,
                                    comp_dis, lista_coeficiente['l_coe'][i + 1][0][k][0],
                                    lista_coeficiente['l_coe'][i + 1][0][k][1], lista_coeficiente['l_coe'][i + 1][0][k][2])

                coeficiente.append(copy.deepcopy(CoeficientesEntrada(lista_coeficiente['l_coe'][i + 1][0][k][0],
                                                                    lista_coeficiente['l_coe'][i + 1][0][k][1],
                                                                    comp_C,
                                                                    copy.deepcopy(coef),
                                                                    i)))
        else:
            coeficiente = [CoeficientesEntrada(None, None, 0.0, Coeficientes(0, False, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), i)]
    
        
        geometria = []
        for j in range(lista_parametros['l_q_s'][i] + 1):
            comp_g = menor_dist(lat_dis, long_dis,
                                comp_dis, lista_parametros['l_sc'][i][j][0],
                                lista_parametros['l_sc'][i][j][1], lista_parametros['l_sc'][i][j][2])
            
            geometria.append(copy.deepcopy(SeccaoTransversal(lista_parametros['l_sc'][i][j][0],
                                                             lista_parametros['l_sc'][i][j][1],
                                                             comp_g,
                                                             lista_parametros['l_sc'][i][j][4],
                                                             lista_parametros['l_sc'][i][j][5],
                                                             lista_parametros['l_sc'][i][j][3],
                                                             lista_parametros['l_sc'][i][j][6])))
        

        
        conc = Concentracoes([0], [0], [0], [0], [0],
                             [0], [0], [0], [0], [0])
   
        # Entradas Pontuais
        if lista_modelagem['m_od']:
            id_od = list_name.index('OD (mg/L)')
            conc.conc_od = np.array(lista_parametros['l_v_i'][i][id_od])
            id_dbo = list_name.index('DBO (mg/L)')
            conc.conc_dbo = np.array(lista_parametros['l_v_i'][i][id_dbo])
        if lista_modelagem['m_n']:
            id_no = list_name.index('N-org (mg/L)')
            conc.conc_no = np.array(lista_parametros['l_v_i'][i][id_no])
            id_n_amon = list_name.index('N-amon (mg/L)')
            conc.conc_n_amon = np.array(lista_parametros['l_v_i'][i][id_n_amon])
            id_nitrito = list_name.index('N-nitri (mg/L)')
            conc.conc_nitrito = np.array(lista_parametros['l_v_i'][i][id_nitrito])
            id_nitrato = list_name.index('N-nitra (mg/L)')
            conc.conc_nitrato = np.array(lista_parametros['l_v_i'][i][id_nitrato])
        if lista_modelagem['m_p']:
            id_p_org = list_name.index('P-org (mg/L)')
            conc.conc_p_org = np.array(lista_parametros['l_v_i'][i][id_p_org])
            id_p_inorg = list_name.index('P-inorg (mg/L)')
            conc.conc_p_inorg = np.array(lista_parametros['l_v_i'][i][id_p_inorg])
            conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
        if lista_modelagem['m_c']:
            id_e_coli = list_name.index('E-coli (NMP/100ml)')
            conc.conc_e_coli = np.array(lista_parametros['l_v_i'][i][id_e_coli])

        id = 1 if lista_modelagem['s_t'] else 0
        id_q = id
                
        conc_ep = [copy.deepcopy(EntradaPontual(lista_parametros['l_la'][i][0],
                                                lista_parametros['l_lo'][i][0],
                                                0.0,
                                                copy.deepcopy(conc),
                                                np.array(lista_parametros['l_v_i'][i][id_q]),
                                                'Início',
                                                i))]
        
        id_q = 0
        # Entradas Pontuais
        if lista_contr_retir['l_q'][i][4]:

            for p in range(lista_contr_retir['l_q'][i][1]):

                
                if lista_modelagem['m_od']:
                    conc.conc_od = np.array(lista_contr_retir['l_ep'][i][p][1][id_od - id])
                    conc.conc_dbo = np.array(lista_contr_retir['l_ep'][i][p][1][id_dbo - id])
                if lista_modelagem['m_n']:
                    conc.conc_no = np.array(lista_contr_retir['l_ep'][i][p][1][id_no - id])
                    conc.conc_n_amon = np.array(lista_contr_retir['l_ep'][i][p][1][id_n_amon - id])
                    conc.conc_nitrito = np.array(lista_contr_retir['l_ep'][i][p][1][id_nitrito - id])
                    conc.conc_nitrato = np.array(lista_contr_retir['l_ep'][i][p][1][id_nitrato - id])
                if lista_modelagem['m_p']:
                    conc.conc_p_org = np.array(lista_contr_retir['l_ep'][i][p][1][id_p_org - id])
                    conc.conc_p_inorg = np.array(lista_contr_retir['l_ep'][i][p][1][id_p_inorg - id])
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem['m_c']:
                    conc.conc_e_coli = np.array(lista_contr_retir['l_ep'][i][p][1][id_e_coli - id])

                comp_ep = menor_dist(lat_dis, long_dis,
                                     comp_dis, lista_contr_retir['l_ep'][i][p][0][1],
                                     lista_contr_retir['l_ep'][i][p][0][2], lista_contr_retir['l_ep'][i][p][0][3])
                
                conc_ep.append(copy.deepcopy(EntradaPontual(lista_contr_retir['l_ep'][i][p][0][1],
                                                            lista_contr_retir['l_ep'][i][p][0][2],
                                                            comp_ep,
                                                            copy.deepcopy(conc),
                                                            np.array(lista_contr_retir['l_ep'][i][p][1][id_q]),
                                                            lista_contr_retir['l_ep'][i][p][0][0],
                                                            i)))

        # Entradas Difusas
        conc_ed = []
        if lista_contr_retir['l_q'][i][5]:
            for d in range(lista_contr_retir['l_q'][i][2]):
                
                if lista_modelagem['m_od']:
                    conc.conc_od = np.array(lista_contr_retir['l_ed'][i][d][1][id_od - id])
                    conc.conc_dbo = np.array(lista_contr_retir['l_ed'][i][d][1][id_dbo - id])
                if lista_modelagem['m_n']:
                    conc.conc_no = np.array(lista_contr_retir['l_ed'][i][d][1][id_no - id])
                    conc.conc_n_amon = np.array(lista_contr_retir['l_ed'][i][d][1][id_n_amon - id])
                    conc.conc_nitrito = np.array(lista_contr_retir['l_ed'][i][d][1][id_nitrito - id])
                    conc.conc_nitrato = np.array(lista_contr_retir['l_ed'][i][d][1][id_nitrato - id])
                if lista_modelagem['m_p']:
                    conc.conc_p_org = np.array(lista_contr_retir['l_ed'][i][d][1][id_p_org - id])
                    conc.conc_p_inorg = np.array(lista_contr_retir['l_ed'][i][d][1][id_p_inorg - id])
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem['m_c']:
                    conc.conc_e_coli = np.array(lista_contr_retir['l_ed'][i][d][1][id_e_coli - id])


                comp_ed_i = menor_dist(lat_dis, long_dis,
                                       comp_dis, lista_contr_retir['l_ed'][i][d][0][1],
                                       lista_contr_retir['l_ed'][i][d][0][3], lista_contr_retir['l_ed'][i][d][0][5])
                comp_ed_f = menor_dist(lat_dis, long_dis,
                                       comp_dis, lista_contr_retir['l_ed'][i][d][0][2],
                                       lista_contr_retir['l_ed'][i][d][0][4], lista_contr_retir['l_ed'][i][d][0][6])

                conc_ed.append(copy.deepcopy(EntradaDifusa(lista_contr_retir['l_ed'][i][d][0][1],
                                                            lista_contr_retir['l_ed'][i][d][0][3],
                                                            lista_contr_retir['l_ed'][i][d][0][2],
                                                            lista_contr_retir['l_ed'][i][d][0][4],
                                                            comp_ed_i,
                                                            comp_ed_f,
                                                            copy.deepcopy(conc),
                                                            np.array(lista_contr_retir['l_ed'][i][d][1][id_q]),
                                                            lista_contr_retir['l_ed'][i][d][0][0],
                                                            i)))


        # Saídas Pontuais
        conc_r = []
        if lista_contr_retir['l_q'][i][3]:
            for r in range(lista_contr_retir['l_q'][i][0]):
                
                comp_r = menor_dist(lat_dis, long_dis,
                                    comp_dis, lista_contr_retir['l_r'][i][r][0][1],
                                    lista_contr_retir['l_r'][i][r][0][2], lista_contr_retir['l_r'][i][r][0][3])

                conc_r.append(copy.deepcopy(SaidaPontual(lista_contr_retir['l_r'][i][r][0][1],
                                                         lista_contr_retir['l_r'][i][r][0][2],
                                                         comp_r,
                                                         np.array(lista_contr_retir['l_r'][i][r][1][id_q]),
                                                         lista_contr_retir['l_r'][i][r][0][0],
                                                         i)))


        # Dados reais
        
        conc_dr = []
        if lista_coeficiente['calb_trib'][i]:
            for dr in range(lista_dados_reais['n_pontos'][marcador_calib]):
                
                if lista_modelagem['s_t']:
                    conj_data = list(lista_dados_reais['l_dr'][marcador_calib][dr][2][0])
                else:
                    conj_data = []
                if lista_modelagem['m_od']:
                    conc.conc_od = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_od - id])
                    conc.conc_dbo = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_dbo - id])
                if lista_modelagem['m_n']:
                    conc.conc_no = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_no - id])
                    conc.conc_n_amon = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_n_amon - id])
                    conc.conc_nitrito = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_nitrito - id])
                    conc.conc_nitrato = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_nitrato - id])
                if lista_modelagem['m_p']:
                    conc.conc_p_org = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_p_org - id])
                    conc.conc_p_inorg = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_p_inorg - id])
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem['m_c']:
                    conc.conc_e_coli = np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_e_coli - id])

                comp_dr = menor_dist(lat_dis, long_dis,
                                     comp_dis, lista_dados_reais['l_dr'][marcador_calib][dr][0][1],
                                     lista_dados_reais['l_dr'][marcador_calib][dr][0][2], lista_dados_reais['l_dr'][marcador_calib][dr][0][3])
                                     
                
                conc_dr.append(copy.deepcopy(DadosReais(lista_dados_reais['l_dr'][marcador_calib][dr][0][1],
                                                            lista_dados_reais['l_dr'][marcador_calib][dr][0][2],
                                                            comp_dr,
                                                            copy.deepcopy(conc),
                                                            conj_data,
                                                            np.array(lista_dados_reais['l_dr'][marcador_calib][dr][1][id_q]),
                                                            lista_dados_reais['l_dr'][marcador_calib][dr][0][0],
                                                            i)))
            
            marcador_calib += 1


        list_tranfor.append(copy.deepcopy(GeralCalib(geometria,
                                                     coeficiente,
                                                     conc_r,
                                                     conc_ep,
                                                     conc_ed,
                                                     conc_dr,
                                                     hidraulica,
                                                     i,
                                                     lista_parametros['l_d'][i])))

    return list_tranfor


def lista_hidraulica(lista_rio, ordem_modelagem, ordem_desague, ponto_af):
    lista_rio_too = copy.deepcopy(lista_rio)
    lista_hidr_final = []
    for ior in ordem_modelagem:

        dados = lista_rio_too[ior]
        lista_hidr_model = func_hidraulica(dados.lista_hidraulica, dados.lista_s_pontual,
                                            dados.lista_e_pontual, dados.lista_e_difusa,
                                            dados.lista_s_transversal, dados.discretizacao)
        lista_hidr_final.append(lista_hidr_model)
        
        if ior != 0:
            comp = menor_dist2(lista_rio_too[ordem_desague[ior - 1]], ponto_af[ior - 1][1],
                               ponto_af[ior - 1][2], ponto_af[ior - 1][3])

            afluente = EntradaPontual(ponto_af[ior - 1][1], ponto_af[ior - 1][2],
                                      comp, None, lista_hidr_model[-1].hidraulica.vazao, ponto_af[ior - 1][0], None)
            
            lista_rio_too[ordem_desague[ior - 1]].lista_e_pontual.append(copy.deepcopy(afluente))
    

    
    return lista_hidr_final


def plot_map(maps, df_new, colun, title, inverse_b):
    
    maps.add_trace(
        go.Scattermapbox(lon=df_new['lon'], lat=df_new['lat'], name=title,
                        marker={"autocolorscale": False,
                                "showscale":True, "size": 6, "opacity": 0.8,
                                "color": colun, "colorscale": 'haline',
                                "colorbar": dict(orientation='h')},
                        marker_reversescale=inverse_b))
    
    return


def ordem_desague_geral(ordem_desague, n_trib, lista_coeficiente, lista_dados_reais, list_tranfor, ponto_af):
    if n_trib > 0:
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

    dict_ordem_grupo = {}

    for id_rio in ordem_modelagem:
        dict_ordem_grupo[str(id_rio)] = []
    
    for id_rio in ordem_modelagem:
        if lista_coeficiente['calb_trib'][id_rio] == True or id_rio == 0:

            dict_ordem_grupo[str(id_rio)].append(id_rio)

        else:
            id_efluente = ordem_desague[id_rio - 1]
            marcador = True
            while marcador:
                
                if lista_coeficiente['calb_trib'][id_efluente]:
                    dict_ordem_grupo[str(id_efluente)].append(id_rio)
                    marcador = False
                
                else:
                    id_efluente = ordem_desague[id_efluente - 1]
    
    ordem_final = []
    for id_rio in ordem_modelagem:
        if dict_ordem_grupo[str(id_rio)] != []:
            ordem_final.append(dict_ordem_grupo[str(id_rio)])  

    list_ids_ordenados_coef = []
    list_lista_grupo_coef_final = []
    lista_conj_calib_final = []

    for conj_calb in ordem_final:
        comp_pts_coef = []
        comp_pts_dr = []
        dict_grupo_coef = {}
        comp_final_rio = list_tranfor[conj_calb[-1]].lista_hidraulica[-1].comprimento

        # Organização da ordem dos coeficientes e dados reais do rio que será calibrado
        for coef_id in range(lista_coeficiente['l_n_p'][conj_calb[-1]] + 1):
            dict_grupo_coef[str(coef_id)] = []
            comp_pts_coef.append(list_tranfor[conj_calb[-1]].lista_e_coeficientes[coef_id].comprimento)
        pares_ordenados_coef = sorted(zip(comp_pts_coef, range(len(comp_pts_coef))), key=lambda x: x[0])
        valores_ordenados_coef, ids_ordenados_coef = zip(*pares_ordenados_coef)
        valores_ordenados_coef = list(valores_ordenados_coef)
        ids_ordenados_coef = list(ids_ordenados_coef)
        list_ids_ordenados_coef.append(list(ids_ordenados_coef))

        for coef_id in range(lista_dados_reais['n_pontos'][conj_calb[-1]]):
            comp_pts_dr.append(list_tranfor[conj_calb[-1]].lista_dados_reais[coef_id].comprimento)
        pares_ordenados_dr = sorted(zip(comp_pts_dr, range(len(comp_pts_dr))), key=lambda x: x[0])
        valores_ordenados_dr, ids_ordenados_dr = zip(*pares_ordenados_dr)
        valores_ordenados_dr = list(valores_ordenados_dr)
        ids_ordenados_dr = list(ids_ordenados_dr)

        # Verificação se o coeficiente possui dados reais para calibração
        lista_grupo_coef_final = []
        for id_coef in range(len(valores_ordenados_coef)):
            lista_grupo_coef = []
            if id_coef != (len(valores_ordenados_coef) - 1):
                comp_post = valores_ordenados_coef[id_coef + 1]
            else:
                comp_post = comp_final_rio
            
            for id_dr in range(len(valores_ordenados_dr)):

                if valores_ordenados_coef[id_coef] < valores_ordenados_dr[id_dr] <= comp_post:
                    lista_grupo_coef.append(ids_ordenados_dr[id_dr])
                    
            lista_grupo_coef_final.append(lista_grupo_coef)
        list_lista_grupo_coef_final.append(lista_grupo_coef_final)

        # Direcionamente dos afluentes para o conjunto que será calibrado
        for rio_conj in conj_calb:
            
            if lista_coeficiente['calb_trib'][rio_conj] == False and rio_conj != 0:
                comp = menor_dist2(list_tranfor[ordem_desague[rio_conj - 1]], ponto_af[rio_conj - 1][1],
                                ponto_af[rio_conj - 1][2], ponto_af[rio_conj - 1][3])

                id_efluente = ordem_desague[rio_conj - 1]

                marcador = True
                while marcador:
                    if lista_coeficiente['calb_trib'][id_efluente]:

                        for id_coef in range(len(valores_ordenados_coef)):
                            
                            if id_coef != (len(valores_ordenados_coef) - 1):
                                comp_post = valores_ordenados_coef[id_coef + 1]
                            else:
                                comp_post = comp_final_rio
                            
                            if valores_ordenados_coef[id_coef] <= comp < comp_post:
                                dict_grupo_coef[str(ids_ordenados_coef[id_coef])].append(rio_conj)

                        marcador = False
                
                    else:
                        id_efluente = ordem_desague[id_efluente - 1]

        list_grupo_coef = []
        for id_coef_rio in ids_ordenados_coef:
            if dict_grupo_coef[str(id_coef_rio)] != []:
                list_grupo_coef.append(dict_grupo_coef[str(id_coef_rio)])  

        lista_conj_calib_final.append(list_grupo_coef)

    return ordem_modelagem, ordem_final, list_ids_ordenados_coef, list_lista_grupo_coef_final, lista_conj_calib_final


def porcent(movel, fixo):
    pc = ((movel * 100) / fixo) - 100

    return pc


def ordem_analise_sensibilidade(list_tranfor, ponto_af, lista_modelagem, ordem_desague,
                                lista_hidr_model, ordem_modelagem):


    an_ses = st.toggle("Gerar a análise de sensibilidade dos coeficientes, com base o intervalo fornecido no Rio Principal.")

    if an_ses:
        par_as = st.expander(":grey[Ajuste no intervalo de busca (Opcional).]")

        par_as.write('Porcentagem de busca na média de cada coeficiente:')
        
        porcentagem = 10
        porcentagem = par_as.slider('porcentagem', 1, 100, 10)


        coef_max_min = copy.deepcopy(list_tranfor[0].lista_e_coeficientes[0].coeficientes)
        
        conj_coeficientes = Coeficientes(0, False, False, 0, 0, 0, 0,
                                        0, 0, 0, 0, 0, 0, 0,
                                        0, 0, 0, 0, 0, 0)
        
        media_coef = Coeficientes(0, False, False, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0)

        lista_chaves = []
        labels_modelos = []
        if lista_modelagem['m_od']:
            conj_coeficientes.k_1, media_coef.k_1 = ajust_porc(coef_max_min.k_1, porcentagem)
            conj_coeficientes.k_2, media_coef.k_2 = ajust_porc(coef_max_min.k_2, porcentagem)
            conj_coeficientes.k_d, media_coef.k_d = ajust_porc(coef_max_min.k_d, porcentagem)
            conj_coeficientes.k_s, media_coef.k_s = ajust_porc(coef_max_min.k_s, porcentagem)
            conj_coeficientes.l_rd, media_coef.l_rd = ajust_porc(coef_max_min.l_rd, porcentagem)
            conj_coeficientes.s_d, media_coef.s_d = ajust_porc(coef_max_min.s_d, porcentagem)
            lista_chaves.extend(['k_1', 'k_2', 'k_d', 'k_s', 'l_rd', 's_d'])
            labels_modelos.extend(['Modelo OD', 'Modelo DBO'])
        if lista_modelagem['m_n']:
            conj_coeficientes.k_oa, media_coef.k_oa = ajust_porc(coef_max_min.k_oa, porcentagem)
            conj_coeficientes.k_so, media_coef.k_so = ajust_porc(coef_max_min.k_so, porcentagem)
            conj_coeficientes.k_an, media_coef.k_an = ajust_porc(coef_max_min.k_an, porcentagem)
            conj_coeficientes.s_amon, media_coef.s_amon = ajust_porc(coef_max_min.s_amon, porcentagem)
            conj_coeficientes.k_nn, media_coef.k_nn = ajust_porc(coef_max_min.k_nn, porcentagem)
            conj_coeficientes.k_nit_od, media_coef.k_nit_od = ajust_porc(coef_max_min.k_nit_od, porcentagem)
            lista_chaves.extend(['k_oa', 'k_so', 'k_an', 's_amon', 'k_nn', 'k_nit_od'])
            labels_modelos.extend(['Modelo NO', 'Modelo N-amon', 'Modelo N-nitrato', 'Modelo N-nitrito'])
        if lista_modelagem['m_od'] == True and lista_modelagem['m_n'] == True:
            conj_coeficientes.r_o2_amon, media_coef.r_o2_amon = ajust_porc(coef_max_min.r_o2_amon, porcentagem)
            lista_chaves.append('r_o2_amon')
        if lista_modelagem['m_p']:
            conj_coeficientes.k_oi, media_coef.k_oi = ajust_porc(coef_max_min.k_oi, porcentagem)
            conj_coeficientes.k_spo, media_coef.k_spo = ajust_porc(coef_max_min.k_spo, porcentagem)
            conj_coeficientes.s_pinorg, media_coef.s_pinorg = ajust_porc(coef_max_min.s_pinorg, porcentagem)
            lista_chaves.extend(['k_oi', 'k_spo', 's_pinorg'])
            labels_modelos.append('Modelo P-total')
        if lista_modelagem['m_c']:
            conj_coeficientes.k_b, media_coef.k_b = ajust_porc(coef_max_min.k_b, porcentagem)
            lista_chaves.append('k_b')
            labels_modelos.append('Modelo Coliformes')
        conj_coeficientes.temperatura, media_coef.temperatura = ajust_porc(coef_max_min.temperatura, porcentagem)
        lista_chaves.append('temperatura')

        result_media, _ = modelagem_as_final('temperatura', lista_hidr_model,  media_coef, list_tranfor, lista_modelagem,
                                          ordem_modelagem, ordem_desague, ponto_af, None, media_coef)
        
        coef_od = ['k_1', 'k_2', 'k_d', 'k_s', 'l_rd', 's_d', 'r_o2_amon', 'k_oa', 'k_so', 'k_an', 's_amon', 'k_nn', 'k_nit_od', 'temperatura']
        coef_n = ['k_oa', 'k_so', 'k_an', 's_amon', 'k_nn', 'k_nit_od', 'temperatura']
        coef_p = ['k_oi', 'k_spo', 's_pinorg', 'temperatura']
        coef_cf = ['k_b', 'temperatura']
        
        variacao_parametro = [-porcentagem, porcentagem]
        lista_as_od = {'PORC': variacao_parametro}
        lista_as_dbo = {'PORC': variacao_parametro}
        lista_as_no = {'PORC': variacao_parametro}
        lista_as_n_amon = {'PORC': variacao_parametro}
        lista_as_nitrato = {'PORC': variacao_parametro}
        lista_as_nitrito = {'PORC': variacao_parametro}
        lista_as_p_total = {'PORC': variacao_parametro}
        lista_as_e_coli = {'PORC': variacao_parametro}


        for id_v in range(2):                      

            partial_function = partial(modelagem_as_final,
                                        lista_hidr_model=lista_hidr_model,
                                        lista_media_coef=media_coef,
                                        lista_rio=list_tranfor,
                                        lista_modelagem=lista_modelagem,
                                        ordem_modelagem=ordem_modelagem,
                                        ordem_desague=ordem_desague,
                                        ponto_af=ponto_af,
                                        i_coef=id_v,
                                        conj_coeficientes=conj_coeficientes)
            
            with ThreadPoolExecutor() as executor:
                
                # futuros = {executor.submit(partial_function, valor): idx for idx, valor in enumerate(lista_chaves)}
                resultados = list(executor.map(partial_function, lista_chaves))

            for futuro in resultados:
                resultado, chave = futuro.result() 

                if id_v == 0:
                    if lista_modelagem['m_od'] and (chave in coef_od):
                        lista_as_od[chave] = [porcent(copy.deepcopy(resultado.conc_od[0]), result_media.conc_od[0])]
                        lista_as_dbo[chave] = [porcent(copy.deepcopy(resultado.conc_dbo[0]), result_media.conc_dbo[0])]
                    if (lista_modelagem['m_n']) and (chave in coef_n):
                        lista_as_no[chave] = [porcent(copy.deepcopy(resultado.conc_no[0]), result_media.conc_no[0])]
                        lista_as_n_amon[chave] = [porcent(copy.deepcopy(resultado.conc_n_amon[0]), result_media.conc_n_amon[0])]
                        lista_as_nitrato[chave] = [porcent(copy.deepcopy(resultado.conc_nitrato[0]), result_media.conc_nitrato[0])]
                        lista_as_nitrito[chave] = [porcent(copy.deepcopy(resultado.conc_nitrito[0]), result_media.conc_nitrito[0])]
                    if (lista_modelagem['m_p']) and (chave in coef_p):
                        lista_as_p_total[chave] = [porcent(copy.deepcopy(resultado.conc_p_total[0]), result_media.conc_p_total[0])]
                    if (lista_modelagem['m_c']) and (chave in coef_cf):
                        lista_as_e_coli[chave] = [porcent(copy.deepcopy(resultado.conc_e_coli[0]), result_media.conc_e_coli[0])]
                else:
                    if lista_modelagem['m_od'] and (chave in coef_od):
                        lista_as_od[chave].append(porcent(copy.deepcopy(resultado.conc_od[0]), result_media.conc_od[0]))
                        lista_as_dbo[chave].append(porcent(copy.deepcopy(resultado.conc_dbo[0]), result_media.conc_dbo[0]))
                    if (lista_modelagem['m_n']) and (chave in coef_n):
                        lista_as_no[chave].append(porcent(copy.deepcopy(resultado.conc_no[0]), result_media.conc_no[0]))
                        lista_as_n_amon[chave].append(porcent(copy.deepcopy(resultado.conc_n_amon[0]), result_media.conc_n_amon[0]))
                        lista_as_nitrato[chave].append(porcent(copy.deepcopy(resultado.conc_nitrato[0]), result_media.conc_nitrato[0]))
                        lista_as_nitrito[chave].append(porcent(copy.deepcopy(resultado.conc_nitrito[0]), result_media.conc_nitrito[0]))
                    if (lista_modelagem['m_p']) and (chave in coef_p):
                        lista_as_p_total[chave].append(porcent(copy.deepcopy(resultado.conc_p_total[0]), result_media.conc_p_total[0]))
                    if (lista_modelagem['m_c']) and (chave in coef_cf):
                        lista_as_e_coli[chave].append(porcent(copy.deepcopy(resultado.conc_e_coli[0]), result_media.conc_e_coli[0]))
        
        tabs_modelo = st.tabs(labels_modelos)
        if lista_modelagem['m_od']:
            tabs_modelo[labels_modelos.index('Modelo OD')].line_chart(lista_as_od, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=500, width=450, use_container_width=False)
            tabs_modelo[labels_modelos.index('Modelo DBO')].line_chart(lista_as_dbo, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=550, width=420, use_container_width=False)
            
        if lista_modelagem['m_n']:
            tabs_modelo[labels_modelos.index('Modelo NO')].line_chart(lista_as_no, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=550, width=420, use_container_width=False)
            tabs_modelo[labels_modelos.index('Modelo N-amon')].line_chart(lista_as_n_amon, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=550, width=420, use_container_width=False)
            tabs_modelo[labels_modelos.index('Modelo N-nitrato')].line_chart(lista_as_nitrato, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=550, width=420, use_container_width=False)
            tabs_modelo[labels_modelos.index('Modelo N-nitrito')].line_chart(lista_as_nitrito, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=550, width=420, use_container_width=False)
            
        if lista_modelagem['m_p']:
            tabs_modelo[labels_modelos.index('Modelo P-total')].line_chart(lista_as_p_total, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=550, width=420, use_container_width=False)
            
        if lista_modelagem['m_c']:
            tabs_modelo[labels_modelos.index('Modelo Coliformes')].line_chart(lista_as_e_coli, x='PORC', 
                          x_label="Variação do coeficiente (%)",
                          y_label="Variação concentração (%)",
                          height=550, width=420, use_container_width=False)
            

    fixar_coef = Coeficientes(0, False, False, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0, 0,
                                  0, 0, 0, 0, 0, 0)
    seq_coef = []

    container2 = st.container(border=True)
    container2.markdown(":grey[Deseja fixar um ou mais coeficiente?]")
    col_1, col_2, col_3, col_4 = container2.columns(4)
    if lista_modelagem['m_od']:
        col_1.write('OD e DBO')
        b_k1 = col_1.toggle('k1')
        if b_k1:
            fixar_coef.k_1 = col_1.number_input('Fixar k1 em:')
        else:
            seq_coef.append('k_1')

        b_k2 = col_1.toggle('k2')
        if b_k2:
            fixar_coef.k_2 = col_1.number_input('Fixar k2 em:')
        else:
            seq_coef.append('k_2')

        b_kd = col_1.toggle('kd')
        if b_kd:
            fixar_coef.k_d = col_1.number_input('Fixar kd em:')
        else:
            seq_coef.append('k_d')

        b_ks = col_1.toggle('ks')
        if b_ks:
            fixar_coef.k_s = col_1.number_input('Fixar ks em:')
        else:
            seq_coef.append('k_s')

        b_lrd = col_1.toggle('lrd')
        if b_lrd:
            fixar_coef.l_rd = col_1.number_input('Fixar lrd em:')
        else:
            seq_coef.append('l_rd')

        b_sd = col_1.toggle('Sd')
        if b_sd:
            fixar_coef.s_d = col_1.number_input('Fixar sd em:')
        else:
            seq_coef.append('s_d')

    if lista_modelagem['m_n']:
        col_3.write('N')
        b_koa = col_3.toggle('koa')
        if b_koa:
            fixar_coef.k_oa = col_3.number_input('Fixar koa em:')
        else:
            seq_coef.append('k_oa')

        b_kso = col_3.toggle('kso')
        if b_kso:
            fixar_coef.k_so = col_3.number_input('Fixar kso em:')
        else:
            seq_coef.append('k_so')

        b_kan = col_3.toggle('kan')
        if b_kan:
            fixar_coef.k_an = col_3.number_input('Fixar kan em:')
        else:
            seq_coef.append('k_an')

        b_Snamon = col_3.toggle('Snamon')
        if b_Snamon:
            fixar_coef.s_amon = col_3.number_input('Fixar Snamon em:')
        else:
            seq_coef.append('s_amon')

        b_knn = col_3.toggle('knn')
        if b_knn:
            fixar_coef.k_nn = col_3.number_input('Fixar knn em:')
        else:
            seq_coef.append('k_nn')

        b_knitr = col_3.toggle('knitr')
        if b_knitr:
            fixar_coef.k_nit_od = col_3.number_input('Fixar knitr em:')
        else:
            seq_coef.append('k_nit_od')

    if lista_modelagem['m_od'] == True and lista_modelagem['m_n'] == True:
        b_O2namon = col_3.toggle('O2namon')
        if b_O2namon:
            fixar_coef.r_o2_amon = col_3.number_input('Fixar O2namon em:')
        else:
            seq_coef.append('r_o2_amon')

    if lista_modelagem['m_p']:
        col_2.write('P')
        b_koi = col_2.toggle('koi')
        if b_koi:
            fixar_coef.k_oi = col_2.number_input('Fixar koi em:')
        else:
            seq_coef.append('k_oi')

        b_kspo = col_2.toggle('kspo')
        if b_kspo:
            fixar_coef.k_spo = col_2.number_input('Fixar kspo em:')
        else:
            seq_coef.append('k_spo')

        b_spinorg = col_2.toggle('Spinorg')
        if b_spinorg:
            fixar_coef.s_pinorg = col_2.number_input('Fixar Spinorg em:')
        else:
            seq_coef.append('s_pinorg')

    if lista_modelagem['m_c']:
        col_4.write('Coli-f')
        b_kb = col_4.toggle('kb')
        if b_kb:
            fixar_coef.k_b = col_4.number_input('Fixar kb em:')
        else:
            seq_coef.append('k_b')

    col_4.write('Geral')
    b_temp = col_4.toggle('Temperatura')
    if b_temp:
        fixar_coef.temperatura = col_4.number_input('Fixar Temperatura em:')
    else:
        seq_coef.append('temperatura')

    
    return fixar_coef, seq_coef



def ajuste_trecho(list_tranfor, lista_hidr_model, list_ordem_coef, marcador_conj_global, marcador_conj_interno,
                  ordem_final, ordem_modelagem):
    
    id_rio_calb = ordem_final[marcador_conj_global][-1]
    if len(list_ordem_coef[marcador_conj_global]) == 1:
        trecho_hidr = copy.deepcopy(lista_hidr_model[ordem_modelagem.index(id_rio_calb)])
    

    else:
        id_coef_atual = list_ordem_coef[marcador_conj_global][marcador_conj_interno]
        comp_atual = list_tranfor[id_rio_calb].lista_e_coeficientes[id_coef_atual].comprimento
        
        if id_coef_atual == list_ordem_coef[marcador_conj_global][-1]:
            comp_post = lista_hidr_model[ordem_modelagem.index(id_rio_calb)][-1].hidraulica.comprimento
        else:
            comp_post = list_tranfor[id_rio_calb].lista_e_coeficientes[list_ordem_coef[marcador_conj_global][marcador_conj_interno + 1]].comprimento

        trecho_hidr = []
        
        for item in range(len(lista_hidr_model[ordem_modelagem.index(id_rio_calb)])):
            if comp_atual <= lista_hidr_model[ordem_modelagem.index(id_rio_calb)][item].hidraulica.comprimento <= comp_post:
                trecho_hidr.append(copy.deepcopy(lista_hidr_model[ordem_modelagem.index(id_rio_calb)][item]))

    return trecho_hidr


def estrutura_calibracao(list_tranfor, fixar_coef, seq_coef, list_ordem_coef, list_ordem_dr,
                         marcador_conj_global, marcador_conj_interno, ordem_final,
                         lista_par_pos, ponto_af, lista_modelagem, lista_hidr_model,
                         ordem_desague, trecho_hidr, dias):
    
    id_rio_calb = ordem_final[marcador_conj_global][-1]
    coef_max_min = list_tranfor[id_rio_calb].lista_e_coeficientes[list_ordem_coef[marcador_conj_global][marcador_conj_interno]].coeficientes
    ordem_dr = list_ordem_dr[marcador_conj_global][marcador_conj_interno]
    
    ordem_rio = ordem_final[marcador_conj_global]

    limite_repet = 20
    cont = 0
    g = 0
    ap_ant = 0
    tam_enxame = lista_par_pos[0]
    n_ger = lista_par_pos[1]
    w = lista_par_pos[2]  # Inércia
    c1 = lista_par_pos[3]  # Componente cognitiva (pessoal)
    c2 = lista_par_pos[4]  # Componente social (global)
    # w = 0.7
    # c1 = 2
    # c2 = 1.5
    # tam_enxame = 50
    # n_ger = 100

    random.seed()


    dic_apitoes_ger = {'apt': [], 'ger': []}
    enx, m_ps_gl, m_ap_gl = gera_enxame_inicial(tam_enxame, seq_coef, coef_max_min, list_tranfor, fixar_coef,
                                                ordem_dr, ponto_af, lista_modelagem, lista_hidr_model,
                                                ordem_desague, ordem_rio, trecho_hidr, dias)
    dic_apitoes_ger = dict_obtj(enx, g, dic_apitoes_ger)
    lista_media_aptidao = []
    lista_melhor_aptidao = []
    lista_melhor_seq = []
    media, cr = melhores_resultados(enx)
    lista_media_aptidao.append(media)
    lista_melhor_aptidao.append(cr.aptidao)
    lista_melhor_seq.append(cr.posicao)
    g = 1

    progress_text = "Operação em andamento. Por favor aguarde."
    my_bar = st.progress(0, text=progress_text)
    while cont <= limite_repet and g <= n_ger:
        my_bar.progress(int((g * 100)/ n_ger), text=progress_text)
        if g == 10:
            w  = 0.4

        enx, m_ps_gl, m_ap_gl = pso(enx, w, c1, c2, seq_coef, coef_max_min, list_tranfor, fixar_coef,
                                            ordem_dr, ponto_af, lista_modelagem, lista_hidr_model,
                                            ordem_desague, ordem_rio, trecho_hidr, dias, m_ps_gl, m_ap_gl)
        dic_apitoes_ger = dict_obtj(enx, g, dic_apitoes_ger)
        media, cr = melhores_resultados(enx)
        lista_media_aptidao.append(media)
        lista_melhor_aptidao.append(cr.aptidao)
        lista_melhor_seq.append(cr.posicao)
        if ap_ant == cr.aptidao:
            cont += 1
        else:
            cont = 0
            ap_ant = cr.aptidao
        g += 1
    my_bar.empty()
    container3 = st.container(border=True)
    container3.markdown('''<h6 style='text-align: center;
                        color: LightSkyBlue;
                        '>Gráfico de evolução da otimização por PSO</h6>''',
                        unsafe_allow_html=True)
    container3.line_chart(lista_melhor_aptidao, x_label='Evolução', y_label='Aptidão', use_container_width=True)

    melhor_h = lista_melhor_seq[-1]

    text_sq = ':gray[Valores estimados: '
    atvo = False
    for tx in range(len(melhor_h)):
        if atvo:
            text_sq += ' | '
        text_sq += str(seq_coef[tx]) + ' = ' + str(melhor_h[tx])
        atvo = True
    text_sq += ']'
    container3.markdown(text_sq)


    precisao = 5

    lista_conc_final = modelagem_calib_final(melhor_h, seq_coef, lista_hidr_model,
                                             list_tranfor, lista_modelagem, ordem_rio,
                                             ordem_desague, ponto_af, fixar_coef,
                                             ordem_dr, trecho_hidr)

    list_sim_real = {}
    labels_modelos = []
    if lista_modelagem['m_od']:
        list_sim_real['conc_od'] = {'real':[], 'simulado': []}
        list_sim_real['conc_dbo'] = {'real':[], 'simulado': []}
        labels_modelos.extend(['Modelo OD', 'Modelo DBO'])
    if lista_modelagem['m_n']:
        list_sim_real['conc_no'] = {'real':[], 'simulado': []}
        list_sim_real['conc_n_amon'] = {'real':[], 'simulado': []}
        list_sim_real['conc_nitrito'] = {'real':[], 'simulado': []}
        labels_modelos.extend(['Modelo NO', 'Modelo N-amon', 'Modelo N-nitrito'])
    if lista_modelagem['m_p']:
        list_sim_real['conc_p_org'] = {'real':[], 'simulado': []}
        list_sim_real['conc_p_inorg'] = {'real':[], 'simulado': []}
        labels_modelos.extend(['Modelo P-org', 'Modelo P-inorg'])
    if lista_modelagem['m_c']:
        list_sim_real['conc_e_coli'] = {'real':[], 'simulado': []}
        labels_modelos.append('Modelo Coliformes')

    nome_modelos = list(list_sim_real.keys())

    list_pontos_trecho = []
    if lista_modelagem['s_t']:
        list_date = []
        for id_dias in range(len(dias)):
            for id_dr in range(len(ordem_dr)):
                lista_dador = list_tranfor[ordem_rio[-1]].lista_dados_reais[ordem_dr[id_dr]]
                for id_dia_dr in range(len(lista_dador.data_dr)):
                    if dias[id_dias].date() == lista_dador.data_dr[id_dia_dr].date():
                        
                        list_date.append(dias[id_dias].date())
                        list_pontos_trecho.append(copy.deepcopy(lista_dador.comprimento))
                        if lista_modelagem['m_od']:
                            list_sim_real['conc_od']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_od[id_dia_dr]))
                            list_sim_real['conc_od']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_od[id_dias]))
                            list_sim_real['conc_dbo']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_dbo[id_dia_dr]))
                            list_sim_real['conc_dbo']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_dbo[id_dias]))
                        if lista_modelagem['m_n']:
                            list_sim_real['conc_no']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_no[id_dia_dr]))
                            list_sim_real['conc_no']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_no[id_dias]))
                            list_sim_real['conc_n_amon']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_n_amon[id_dia_dr]))
                            list_sim_real['conc_n_amon']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_n_amon[id_dias]))
                            list_sim_real['conc_nitrito']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_nitrito[id_dia_dr]))
                            list_sim_real['conc_nitrito']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_nitrito[id_dias]))
                        if lista_modelagem['m_p']:
                            list_sim_real['conc_p_org']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_org[id_dia_dr]))
                            list_sim_real['conc_p_org']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_org[id_dias]))
                            list_sim_real['conc_p_inorg']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_inorg[id_dia_dr]))
                            list_sim_real['conc_p_inorg']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_inorg[id_dias]))
                        if lista_modelagem['m_c']:
                            list_sim_real['conc_e_coli']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_e_coli[id_dia_dr]))
                            list_sim_real['conc_e_coli']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_e_coli[id_dias]))
    else:
        for id_dr in range(len(ordem_dr)):
            lista_dador = list_tranfor[ordem_rio[-1]].lista_dados_reais[ordem_dr[id_dr]]
            list_pontos_trecho.append(copy.deepcopy(lista_dador.comprimento))
            if lista_modelagem['m_od']:
                list_sim_real['conc_od']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_od[0]))
                list_sim_real['conc_od']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_od[0]))
                list_sim_real['conc_dbo']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_dbo[0]))
                list_sim_real['conc_dbo']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_dbo[0]))
            if lista_modelagem['m_n']:
                list_sim_real['conc_no']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_no[0]))
                list_sim_real['conc_no']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_no[0]))
                list_sim_real['conc_n_amon']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_n_amon[0]))
                list_sim_real['conc_n_amon']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_n_amon[0]))
                list_sim_real['conc_nitrito']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_nitrito[0]))
                list_sim_real['conc_nitrito']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_nitrito[0]))
            if lista_modelagem['m_p']:
                list_sim_real['conc_p_org']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_org[0]))
                list_sim_real['conc_p_org']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_org[0]))
                list_sim_real['conc_p_inorg']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_inorg[0]))
                list_sim_real['conc_p_inorg']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_inorg[0]))
            if lista_modelagem['m_c']:
                list_sim_real['conc_e_coli']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_e_coli[0]))
                list_sim_real['conc_e_coli']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_e_coli[0]))

    tabs_modelo = st.tabs(labels_modelos)
    
    for idn in range(len(nome_modelos)):
        model = nome_modelos[idn]
        coln_1, conl_2 = tabs_modelo[idn].columns(2)
        soma_1 = 0
        soma_2 = 0
        if len(list_sim_real[model]['simulado']) > 0:
            for id in range(len(list_sim_real[model]['simulado'])):
                soma_1 += (list_sim_real[model]['real'][id] - list_sim_real[model]['simulado'][id])**2
                soma_2 += (list_sim_real[model]['real'][id] - np.mean(list_sim_real[model]['real']))**2

            if len(list_sim_real[model]['simulado']) == 1 or soma_2 == 0:
                f_1 = 1 - (soma_1 / 0.0001)
            else:
                f_1 = 1 - (soma_1 / soma_2)
            
            coln_1.markdown('Coeficiente de Nash-Sutcliffe: ' + str(np.round(f_1, precisao)))
        else:
            coln_1.markdown('ERRO - 9999')

        if lista_modelagem['s_t']:
            df_dict = {'Data': list_date, 'Comprimento': list_pontos_trecho, 'Real': list_sim_real[model]['real'], 'Simulado': list_sim_real[model]['simulado']}
            
        else:
            df_dict = {'Comprimento': list_pontos_trecho, 'Real': list_sim_real[model]['real'], 'Simulado': list_sim_real[model]['simulado']}
        
        coln_1.dataframe(df_dict)
        df = pd.DataFrame(df_dict)
        melted_df = df.melt(id_vars='Comprimento', var_name='Resultado', value_name='Valor')

        chart = alt.Chart(melted_df).mark_point(point=True).encode(
            x=alt.X('Comprimento:Q', title='Comprimento'),
            y=alt.Y('Valor:Q', title='Concentração', scale=alt.Scale(zero=False)),
            color=alt.Color('Resultado:N', legend=alt.Legend(orient='top', title=None)),
            tooltip=['Comprimento', 'Resultado', 'Valor']
        ).properties()

        conl_2.altair_chart(chart, use_container_width=True)
    e_coeficientes = copy.deepcopy(fixar_coef)
    for id_c in range(len(seq_coef)):
        setattr(e_coeficientes, seq_coef[id_c], melhor_h[id_c])

    return e_coeficientes, lista_melhor_aptidao[-1]



def tabelar(lista_modelagem):

    coef_tabelados = Coeficientes(0, False, False, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0, 0,
                                0, 0, 0, 0, 0, 0)

    container4 = st.container(border=True)
    container4.markdown("O modelo adotará os seguintes valores:")
    col_1, col_2, col_3, col_4 = container4.columns(4)
    if lista_modelagem['m_od']:
        col_1.write('OD e DBO')
        coef_tabelados.k_1 = col_1.number_input('Fixar k1 em:', value=0.19)
        coef_tabelados.k_2 = col_1.number_input('Fixar k2 em:', value=40)
        coef_tabelados.k_d = col_1.number_input('Fixar kd em:', value=0.4)
        coef_tabelados.k_s = col_1.number_input('Fixar ks em:', value=2.0)
        coef_tabelados.l_rd = col_1.number_input('Fixar lrd em:', value=0.0)
        coef_tabelados.s_d = col_1.number_input('Fixar sd em:', value=2.86)

    if lista_modelagem['m_n']:
        col_3.write('N')
        coef_tabelados.k_oa = col_3.number_input('Fixar koa em:', value=0.001)
        coef_tabelados.k_so = col_3.number_input('Fixar kso em:', value=0.07)
        coef_tabelados.k_an = col_3.number_input('Fixar kan em:', value=0.4)
        coef_tabelados.s_amon = col_3.number_input('Fixar Snamon em:', value=0.0)
        coef_tabelados.k_nn = col_3.number_input('Fixar knn em:', value=0.05)
        coef_tabelados.k_nit_od = col_3.number_input('Fixar knitr em:', value=0.6)

    if lista_modelagem['m_od'] == True and lista_modelagem['m_n'] == True:
        coef_tabelados.r_o2_amon = col_3.number_input('Fixar O2namon em:', value=3.2)

    if lista_modelagem['m_p']:
        col_2.write('P')
        coef_tabelados.k_oi = col_2.number_input('Fixar koi em:', value=0.6)
        coef_tabelados.k_spo = col_2.number_input('Fixar kspo em:', value=0.0)
        coef_tabelados.s_pinorg = col_2.number_input('Fixar Spinorg em:', value=3.4)

    if lista_modelagem['m_c']:
        col_4.write('Coli-f')
        coef_tabelados.k_b = col_4.number_input('Fixar kb em:', value=0.2)
    
    col_4.write('Geral')
    coef_tabelados.temperatura = col_4.number_input('Fixar Temperatura em:', value=20.0)
    
    return coef_tabelados


