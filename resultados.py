import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from equacoes import lista_hidr, modelagem_Final, menor_dist
import copy
import numpy as np
from plotly.subplots import make_subplots

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
        self.froude = froude


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


def transformacao(lista_modelagem, lista_parametros, lista_coeficiente,
                  lista_contr_retir, list_name):
    
    list_tranfor = []
    

    for i in range(lista_modelagem[6] + 1):

        hidraulica = (lista_hidr(lista_parametros[2][i],
                                 lista_parametros[3][i],
                                 lista_parametros[4][i],
                                 lista_parametros[1][i],
                                 lista_parametros[6][i]))
        
        lat_dis = []
        long_dis = []
        comp_dis = []
        for llc in range(len(hidraulica)):
            lat_dis.append(hidraulica[llc].latitude)
            long_dis.append(hidraulica[llc].longitude)
            comp_dis.append(hidraulica[llc].comprimento)


        coeficiente = []
        for k in range(lista_coeficiente[1][i] + 1):
            k2_calc = False if lista_modelagem[1] else True
            
            coef = Coeficientes(np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('Temperatura (°C)')]),
                                k2_calc, None, None, None,
                                None, None, None, None, None,
                                None, None, None, None, None,
                                None, None, None, None, None)

            if lista_modelagem[1]:
                coef.k_2 = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('k2 (1/d)')])
            if lista_modelagem[1] == False and lista_modelagem[0] == True:
                coef.k_2_max = lista_coeficiente[0][i + 1][k][0][3]
            if lista_modelagem[0]:
                coef.k_1 = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('k1 (1/d)')])
                coef.k_d = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('kd (1/d)')])
                coef.k_s = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('ks (1/d)')])
                coef.l_rd = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('lrd (gDBO5/m.d)')])
                coef.s_d = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('sd (1/d)')])
            if lista_modelagem[0] == True and lista_modelagem[3] == True:
                coef.r_o2_amon = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('O2namon (mgO2/mgNamon oxid)')])
            if lista_modelagem[3]:
                coef.k_oa = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('koa (1/d)')])
                coef.k_so = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('kso (1/d)')])
                coef.k_an = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('kan (1/d)')])
                coef.s_amon = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('Snamon (g/m2.d)')])
                coef.k_nn = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('knn (1/d)')])
                coef.k_nit_od = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('knitr (1/d)')])
            if lista_modelagem[4]:
                coef.k_oi = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('koi (1/d)')])
                coef.k_spo = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('kspo (1/d)')])
                coef.s_pinorg = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('spinorg (1/d)')])
            if lista_modelagem[5]:
                coef.k_b = np.array(lista_coeficiente[0][i + 1][k][1][lista_coeficiente[0][0].index('kb (1/d)')])

            comp_C = menor_dist(lat_dis, long_dis,
                                comp_dis, lista_coeficiente[0][i + 1][k][0][0],
                                lista_coeficiente[0][i + 1][k][0][1], lista_coeficiente[0][i + 1][k][0][2])

            coeficiente.append(copy.deepcopy(CoeficientesEntrada(lista_coeficiente[0][i + 1][k][0][0],
                                                                 lista_coeficiente[0][i + 1][k][0][1],
                                                                 comp_C,
                                                                 copy.deepcopy(coef),
                                                                 i)))
    
        
        geometria = []
        for j in range(lista_parametros[7][i] + 1):
            comp_g = menor_dist(lat_dis, long_dis,
                                comp_dis, lista_parametros[5][i][j][0],
                                lista_parametros[5][i][j][1], lista_parametros[5][i][j][2])
            
            geometria.append(copy.deepcopy(SeccaoTransversal(lista_parametros[5][i][j][0],
                                                             lista_parametros[5][i][j][1],
                                                             comp_g,
                                                             lista_parametros[5][i][j][4],
                                                             lista_parametros[5][i][j][5],
                                                             lista_parametros[5][i][j][3],
                                                             lista_parametros[5][i][j][6])))
        

        
        conc = Concentracoes(None, None, None, None, None,
                             None, None, None, None, None)
   
        # Entradas Pontuais
        if lista_modelagem[0]:
            id_od = list_name.index('OD (mg/L)')
            conc.conc_od = np.array(lista_parametros[0][i][id_od])
            id_dbo = list_name.index('DBO (mg/L)')
            conc.conc_dbo = np.array(lista_parametros[0][i][id_dbo])
        if lista_modelagem[3]:
            id_no = list_name.index('N-org (mg/L)')
            conc.conc_no = np.array(lista_parametros[0][i][id_no])
            id_n_amon = list_name.index('N-amon (mg/L)')
            conc.conc_n_amon = np.array(lista_parametros[0][i][id_n_amon])
            id_nitrito = list_name.index('N-nitri (mg/L)')
            conc.conc_nitrito = np.array(lista_parametros[0][i][id_nitrito])
            id_nitrato = list_name.index('N-nitra (mg/L)')
            conc.conc_nitrato = np.array(lista_parametros[0][i][id_nitrato])
        if lista_modelagem[4]:
            id_p_org = list_name.index('P-org (mg/L)')
            conc.conc_p_org = np.array(lista_parametros[0][i][id_p_org])
            id_p_inorg = list_name.index('P-inorg (mg/L)')
            conc.conc_p_inorg = np.array(lista_parametros[0][i][id_p_inorg])
            conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
        if lista_modelagem[5]:
            id_e_coli = list_name.index('E-coli (NMP/100ml)')
            conc.conc_e_coli = np.array(lista_parametros[0][i][id_e_coli])

        id = 1 if lista_modelagem[7] else 0
        id_q = id
                
        conc_ep = [copy.deepcopy(EntradaPontual(lista_parametros[3][i][0],
                                                lista_parametros[2][i][0],
                                                0.0,
                                                copy.deepcopy(conc),
                                                np.array(lista_parametros[0][i][id_q]),
                                                'Início',
                                                i))]
        
        id_q = 0
        # Entradas Pontuais
        if lista_contr_retir[3][i][4]:

            for p in range(lista_contr_retir[3][i][1]):

                
                if lista_modelagem[0]:
                    conc.conc_od = np.array(lista_contr_retir[1][i][p][1][id_od])
                    conc.conc_dbo = np.array(lista_contr_retir[1][i][p][1][id_dbo])
                if lista_modelagem[3]:
                    conc.conc_no = np.array(lista_contr_retir[1][i][p][1][id_no])
                    conc.conc_n_amon = np.array(lista_contr_retir[1][i][p][1][id_n_amon])
                    conc.conc_nitrito = np.array(lista_contr_retir[1][i][p][1][id_nitrito])
                    conc.conc_nitrato = np.array(lista_contr_retir[1][i][p][1][id_nitrato])
                if lista_modelagem[4]:
                    conc.conc_p_org = np.array(lista_contr_retir[1][i][p][1][id_p_org])
                    conc.conc_p_inorg = np.array(lista_contr_retir[1][i][p][1][id_p_inorg])
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem[5]:
                    conc.conc_e_coli = np.array(lista_contr_retir[1][i][p][1][id_e_coli])

                comp_ep = menor_dist(lat_dis, long_dis,
                                     comp_dis, lista_contr_retir[1][i][p][0][1],
                                     lista_contr_retir[1][i][p][0][2], lista_contr_retir[1][i][p][0][3])
                
                conc_ep.append(copy.deepcopy(EntradaPontual(lista_contr_retir[1][i][p][0][1],
                                                            lista_contr_retir[1][i][p][0][2],
                                                            comp_ep,
                                                            copy.deepcopy(conc),
                                                            np.array(lista_contr_retir[1][i][p][1][id_q]),
                                                            lista_contr_retir[1][i][p][0][0],
                                                            i)))

        # Entradas Difusas
        conc_ed = []
        if lista_contr_retir[3][i][5]:
            for d in range(lista_contr_retir[3][i][2]):
                
                if lista_modelagem[0]:
                    conc.conc_od = np.array(lista_contr_retir[2][i][d][1][id_od])
                    conc.conc_dbo = np.array(lista_contr_retir[2][i][d][1][id_dbo])
                if lista_modelagem[3]:
                    conc.conc_no = np.array(lista_contr_retir[2][i][d][1][id_no])
                    conc.conc_n_amon = np.array(lista_contr_retir[2][i][d][1][id_n_amon])
                    conc.conc_nitrito = np.array(lista_contr_retir[2][i][d][1][id_nitrito])
                    conc.conc_nitrato = np.array(lista_contr_retir[2][i][d][1][id_nitrato])
                if lista_modelagem[4]:
                    conc.conc_p_org = np.array(lista_contr_retir[2][i][d][1][id_p_org])
                    conc.conc_p_inorg = np.array(lista_contr_retir[2][i][d][1][id_p_inorg])
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem[5]:
                    conc.conc_e_coli = np.array(lista_contr_retir[2][i][d][1][id_e_coli])


                comp_ed_i = menor_dist(lat_dis, long_dis,
                                       comp_dis, lista_contr_retir[2][i][d][0][1],
                                       lista_contr_retir[2][i][d][0][3], lista_contr_retir[2][i][d][0][5])
                comp_ed_f = menor_dist(lat_dis, long_dis,
                                       comp_dis, lista_contr_retir[2][i][d][0][2],
                                       lista_contr_retir[2][i][d][0][4], lista_contr_retir[2][i][d][0][6])

                conc_ed.append(copy.deepcopy(EntradaPontual(lista_contr_retir[2][i][d][0][1],
                                                            lista_contr_retir[2][i][d][0][3],
                                                            lista_contr_retir[2][i][d][0][2],
                                                            lista_contr_retir[2][i][d][0][4],
                                                            comp_ed_i,
                                                            comp_ed_f,
                                                            copy.deepcopy(conc),
                                                            np.array(lista_contr_retir[2][i][d][1][id_q]),
                                                            lista_contr_retir[2][i][d][0][0],
                                                            i)))


        # Saídas Pontuais
        conc_r = []
        if lista_contr_retir[3][i][3]:
            for r in range(lista_contr_retir[3][i][0]):
                
                comp_r = menor_dist(lat_dis, long_dis,
                                    comp_dis, lista_contr_retir[0][i][r][0][1],
                                    lista_contr_retir[0][i][r][0][2], lista_contr_retir[0][i][r][0][3])

                conc_r.append(copy.deepcopy(SaidaPontual(lista_contr_retir[0][i][r][0][1],
                                                         lista_contr_retir[0][i][r][0][2],
                                                         comp_r,
                                                         np.array(lista_contr_retir[0][i][r][1][id_q]),
                                                         lista_contr_retir[0][i][r][0][0],
                                                         i)))

        list_tranfor.append(copy.deepcopy(Geral(geometria,
                                                coeficiente,
                                                conc_r,
                                                conc_ep,
                                                conc_ed,
                                                hidraulica,
                                                i,
                                                lista_parametros[6][i])))

    return list_tranfor


def resultados(n_tributarios, list_tranfor, ponto_af, lista_modelagem, ordem_desague, dias):
    st.divider()
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
    
    lista_final, list_entr = modelagem_Final(list_tranfor, ponto_af, lista_modelagem,
                                             ordem_desague, ordem_modelagem)
        
    lidt_df = []
    for r in range(n_tributarios + 1):
        rio = lista_final[r]
        df = None
        obj_to_dict = {'rio': [],'latitude': [], 'longitude': [], 'altitude': [], 'comprimento': [], 'vazao': [],
                        'profundidade': [], 'velocidade': [], 'tensao_c': [], 'nivel_dagua': [],
                        'froude': []}
        if lista_modelagem[7]:
            dt = {'data': []}
            dt.update(obj_to_dict)
            obj_to_dict = dt
        if lista_modelagem[0]:
            obj_to_dict['conc_od'] = []
            obj_to_dict['conc_dbo'] = []
        if lista_modelagem[3]:
            obj_to_dict['conc_no'] = []
            obj_to_dict['conc_n_amon'] = []
            obj_to_dict['conc_nitrito'] = []
            obj_to_dict['conc_nitrato'] = []
        if lista_modelagem[4]:
            obj_to_dict['conc_p_org'] = []
            obj_to_dict['conc_p_inorg'] = []
            obj_to_dict['conc_p_total'] = []
        if lista_modelagem[5]:
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

                if lista_modelagem[7]:
                    obj_to_dict['data'].append(dias[idata])
                if lista_modelagem[0]:
                    obj_to_dict['conc_od'].append(cc.conc_od[idata])
                    obj_to_dict['conc_dbo'].append(cc.conc_dbo[idata])
                if lista_modelagem[3]:
                    obj_to_dict['conc_no'].append(cc.conc_no[idata])
                    obj_to_dict['conc_n_amon'].append(cc.conc_n_amon[idata])
                    obj_to_dict['conc_nitrito'].append(cc.conc_nitrito[idata])
                    obj_to_dict['conc_nitrato'].append(cc.conc_nitrato[idata])
                if lista_modelagem[4]:
                    obj_to_dict['conc_p_org'].append(cc.conc_p_org[idata])
                    obj_to_dict['conc_p_inorg'].append(cc.conc_p_inorg[idata])
                    obj_to_dict['conc_p_total'].append(cc.conc_p_total[idata])
                if lista_modelagem[5]:
                    obj_to_dict['conc_e_coli'].append(cc.conc_e_coli[idata])

        df = pd.DataFrame(obj_to_dict)
        lidt_df.append(df)
    
    return lidt_df, list_entr, ordem_modelagem


def plot_map(maps, df_new, colun, title, inverse_b):
    
    maps.add_trace(
        go.Scattermapbox(lon=df_new['lon'], lat=df_new['lat'], name=title,
                        marker={"autocolorscale": False,
                                "showscale":True, "size": 6, "opacity": 0.8,
                                "color": colun, "colorscale": 'haline',
                                "colorbar": dict(orientation='h')},
                        marker_reversescale=inverse_b))
    
    return


def plotar(n_tributarios, lista_modelagem, lidt_df, list_entr, labels, zona, hemisferio, dias, ordem_modelagem):

    lidt_df.reverse()
    ordem_modelagem.reverse()
    list_tab = ['Gráficos do Rio Principal', 'Tabelas']
    str_lat = str(lidt_df[0]['latitude'][0])
    if str_lat != 'nan' and str_lat != 'None':
        list_tab.append('Representações geoespaciais')

    result_tabs = st.tabs(list_tab)

    with result_tabs[0]:
        if lista_modelagem[7]:
            df = lidt_df[0].loc[lidt_df[0]['data'] == dias[-1]]
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(title_text="Concentrações do dia " + str(dias[-1]),
                                title_font_color="teal")

        else:
            df = lidt_df[0]
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.update_layout(title_text="Concentrações",
                                title_font_color="teal")

        if lista_modelagem[0]:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_od"],
                                mode='lines',
                                name='OD'))
        
        if lista_modelagem[2]:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_dbo"],
                                mode='lines',
                                name='DBO'))
        
        if lista_modelagem[2]:
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
        if lista_modelagem[3]:
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_p_org"],
                                mode='lines',
                                name='P-org'))
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_p_inorg"],
                                mode='lines',
                                name='P-inorg'))
            fig.add_trace(go.Scatter(x=df["comprimento"], y=df["conc_p_total"],
                                mode='lines',
                                name='P total'))
        if lista_modelagem[4]:
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

            if str(list_entr[0 + 1].descricao) == 'nan':

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

            if str(list_entr[0 + 1].descricao) == 'nan' or str(list_entr[0 + 1].descricao) == 'None':

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
            ex = st.expander('Resultados do ' + labels[ordem_modelagem[r1]])
            ex.write(lidt_df[r1])

        df_new = pd.concat(lidt_df)
        if len(lidt_df) > 1:
            ex2 = st.expander('Resultados Agrupado')
            ex2.write(df_new)

    if str_lat != 'nan' and str_lat != 'None':
        with result_tabs[2]:       

            from pyproj import Proj
            
            if lista_modelagem[7]:
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


            if lista_modelagem[0]:
                plot_map(maps, df_new, df_new["conc_od"], 'OD (mg/L)', False)               
            if lista_modelagem[2]:
                plot_map(maps, df_new, df_new["conc_dbo"], 'DBO (mg/L)', True)
            if lista_modelagem[3]:
                plot_map(maps, df_new, df_new["conc_p_org"], 'P-org (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_p_inorg"], 'P-inorg (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_p_total"], 'P total (mg/L)', True)     
            if lista_modelagem[2]:
                plot_map(maps, df_new, df_new["conc_no"], 'N-org (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_n_amon"], 'N-amon (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_nitrato"], 'N-nitri (mg/L)', True)
                plot_map(maps, df_new, df_new["conc_nitrito"], 'N-nitra (mg/L)', True)
            if lista_modelagem[4]:
                plot_map(maps, df_new, df_new["conc_e_coli"], 'E-coli (NMP/100ml)', True)
            st.plotly_chart(maps, use_container_width=True)
    
    return

