import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from equacoes import lista_hidr, modelagem_Final
import copy

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
        self.descricao = descricao
        self.vazao = vazao
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

        coeficiente = []
        for k in range(lista_coeficiente[1][i] + 1):
            if lista_modelagem[1]:
                k2_calc = False
            else:
                k2_calc = True

            coef = Coeficientes(lista_coeficiente[0][i + 1][k][3],
                                k2_calc, None, None, None,
                                None, None, None, None, None,
                                None, None, None, None, None,
                                None, None, None, None, None)


            if lista_modelagem[1]:
                coef.k_2 = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('k2 (1/d)')]
            if lista_modelagem[1] == False and lista_modelagem[0] == True:
                coef.k_2_max = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('k2 máximo (1/d)')]
            if lista_modelagem[0]:
                coef.k_1 = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('k1 (1/d)')]
                coef.k_d = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('kd (1/d)')]
                coef.k_s = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('ks (1/d)')]
                coef.l_rd = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('lrd (gDBO5/m.d)')]
                coef.s_d = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('sd (1/d)')]
            if lista_modelagem[0] == True and lista_modelagem[3] == True:
                coef.r_o2_amon = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('O2namon (mgO2/mgNamon oxid)')]
            if lista_modelagem[3]:
                coef.k_oa = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('koa (1/d)')]
                coef.k_so = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('kso (1/d)')]
                coef.k_an = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('kan (1/d)')]
                coef.s_amon = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('Snamon (g/m2.d)')]
                coef.k_nn = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('knn (1/d)')]
                coef.k_nit_od = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('knitr (1/d)')]
            if lista_modelagem[4]:
                coef.k_oi = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('koi (1/d)')]
                coef.k_spo = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('kspo (1/d)')]
                coef.s_pinorg = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('spinorg (1/d)')]
            if lista_modelagem[5]:
                coef.k_b = lista_coeficiente[0][i + 1][k][lista_coeficiente[0][0].index('kb (1/d)')]

            coeficiente.append(copy.deepcopy(CoeficientesEntrada(lista_coeficiente[0][i + 1][k][0],
                                                                 lista_coeficiente[0][i + 1][k][1],
                                                                 lista_coeficiente[0][i + 1][k][2],
                                                                 copy.deepcopy(coef),
                                                                 i)))

        
        geometria = []
        for j in range(lista_parametros[7][i] + 1):
            geometria.append(copy.deepcopy(SeccaoTransversal(lista_parametros[5][i][j][0],
                                                             lista_parametros[5][i][j][1],
                                                             lista_parametros[5][i][j][2],
                                                             lista_parametros[5][i][j][4],
                                                             lista_parametros[5][i][j][5],
                                                             lista_parametros[5][i][j][3],
                                                             lista_parametros[5][i][j][6])))
        

        hidraulica = (lista_hidr(lista_parametros[2][i],
                                 lista_parametros[3][i],
                                 lista_parametros[4][i],
                                 lista_parametros[1][i],
                                 lista_parametros[6][i]))
        


        conc = Concentracoes(None, None, None, None, 0,
                             None, None, None, None, None)
   
        # Entradas Pontuais
        if lista_modelagem[0]:
            id_od = list_name.index('Oxigênio dissolvido (mg/L)')
            conc.conc_od = lista_parametros[0][i][id_od]
            id_dbo = list_name.index('DBO (mg/L)')
            conc.conc_dbo = lista_parametros[0][i][id_dbo]
        if lista_modelagem[3]:
            id_no = list_name.index('Nitrogênio orgânico (mg/L)')
            conc.conc_no = lista_parametros[0][i][id_no]
            id_n_amon = list_name.index('Amônia (mg/L)')
            conc.conc_n_amon = lista_parametros[0][i][id_n_amon]
            id_nitrito = list_name.index('Nitrito (mg/L)')
            conc.conc_nitrito = lista_parametros[0][i][id_nitrito]
        if lista_modelagem[4]:
            id_p_org = list_name.index('Fósforo orgânico (mg/L)')
            conc.conc_p_org = lista_parametros[0][i][id_p_org]
            id_p_inorg = list_name.index('Fósforo inorgânico (mg/L)')
            conc.conc_p_inorg = lista_parametros[0][i][id_p_inorg]
            conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
        if lista_modelagem[5]:
            id_e_coli = list_name.index('E-coli (NMP/100ml)')
            conc.conc_e_coli = lista_parametros[0][i][id_e_coli]

        conc_ep = [copy.deepcopy(EntradaPontual(lista_parametros[3][i][0],
                                                lista_parametros[2][i][0],
                                                0.0,
                                                copy.deepcopy(conc),
                                                lista_parametros[0][i][0],
                                                'Início',
                                                i))]
        
        if lista_contr_retir[3][i][4]:
            for p in range(lista_contr_retir[3][i][1]):


                if lista_modelagem[0]:
                    conc.conc_od = lista_contr_retir[1][i][p][id_od + 4]
                    conc.conc_dbo = lista_contr_retir[1][i][p][id_dbo + 4]
                if lista_modelagem[3]:
                    conc.conc_no = lista_contr_retir[1][i][p][id_no + 4]
                    conc.conc_n_amon = lista_contr_retir[1][i][p][id_n_amon + 4]
                    conc.conc_nitrito = lista_contr_retir[1][i][p][id_nitrito + 4]
                if lista_modelagem[4]:
                    conc.conc_p_org = lista_contr_retir[1][i][p][id_p_org + 4]
                    conc.conc_p_inorg = lista_contr_retir[1][i][p][id_p_inorg + 4]
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem[5]:
                    conc.conc_e_coli = lista_contr_retir[1][i][p][id_e_coli + 4]

                conc_ep.append(copy.deepcopy(EntradaPontual(lista_contr_retir[1][i][p][1],
                                                            lista_contr_retir[1][i][p][2],
                                                            lista_contr_retir[1][i][p][3],
                                                            copy.deepcopy(conc),
                                                            lista_contr_retir[1][i][p][4],
                                                            lista_contr_retir[1][i][p][0],
                                                            i)))

        # Entradas Difusas
        conc_ed = []
        if lista_contr_retir[3][i][5]:
            for d in range(lista_contr_retir[3][i][2]):

                if lista_modelagem[0]:
                    conc.conc_od = lista_contr_retir[2][i][d][id_od + 7]
                    conc.conc_dbo = lista_contr_retir[2][i][d][id_dbo + 7]
                if lista_modelagem[3]:
                    conc.conc_no = lista_contr_retir[2][i][d][id_no + 7]
                    conc.conc_n_amon = lista_contr_retir[2][i][d][id_n_amon + 7]
                    conc.conc_nitrito = lista_contr_retir[2][i][d][id_nitrito + 7]
                if lista_modelagem[4]:
                    conc.conc_p_org = lista_contr_retir[2][i][d][id_p_org + 7]
                    conc.conc_p_inorg = lista_contr_retir[2][i][d][id_p_inorg + 7]
                    conc.conc_p_total = conc.conc_p_org + conc.conc_p_inorg
                if lista_modelagem[5]:
                    conc.conc_e_coli = lista_contr_retir[2][i][d][id_e_coli + 7]

                conc_ed.append(copy.deepcopy(EntradaPontual(lista_contr_retir[2][i][d][1],
                                                            lista_contr_retir[2][i][d][3],
                                                            lista_contr_retir[2][i][d][2],
                                                            lista_contr_retir[2][i][d][4],
                                                            lista_contr_retir[2][i][d][5],
                                                            lista_contr_retir[2][i][d][6],
                                                            copy.deepcopy(conc),
                                                            lista_contr_retir[2][i][d][7],
                                                            lista_contr_retir[2][i][d][0],
                                                            i)))


        # Saídas Pontuais
        conc_r = []
        if lista_contr_retir[3][i][3]:
            for r in range(lista_contr_retir[3][i][0]):
                
                conc_r.append(copy.deepcopy(EntradaPontual(lista_contr_retir[0][i][r][1],
                                                           lista_contr_retir[0][i][r][2],
                                                           lista_contr_retir[0][i][r][3],
                                                           lista_contr_retir[0][i][r][4],
                                                           lista_contr_retir[0][i][r][0],
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


def resultados(n_tributarios, list_tranfor, ponto_af, lista_modelagem):
    st.divider()
    st.markdown('''<h3 style='text-align: center;
                color: black;
                '>Resultados </h3>''',
                unsafe_allow_html=True)
    list_tranfor.reverse()
    ponto_af.reverse()
    lista_final, list_entr = modelagem_Final(list_tranfor, ponto_af, lista_modelagem)
    
    lidt_df = []
    lista_final.reverse()
    for r in range(n_tributarios + 1):
        rio = lista_final[r]
        df = None
        df = pd.DataFrame(columns=['latitude', 'longitude', 'comprimento', 'vazao', 'rugosidade_n', 'largura_rio', 'altitude',
                    'inclinacao', 'ang_esquerdo', 'ang_direito', 'profundidade', 'velocidade', 'tensao_c', 'nivel_dagua',
                    'froude', 'temperatura', 'k_2', 's_d', 'k_d', 'k_s', 'l_rd', 'k_so',
                    'k_oa', 'k_an', 'k_nn', 's_amon', 'k_spo', 'k_oi', 'k_b', 'r_o2_amon', 'k_nit_od',
                    'conc_od', 'conc_dbo', 'conc_no', 'conc_n_amon', 'conc_nitrato', 'conc_nitrito',
                    'conc_p_org', 'conc_p_inorg', 'conc_p_total', 'conc_e_coli'])

        for i in range(len(rio)):
            h = rio[i].hidraulica
            cf = rio[i].coeficientes
            cc = rio[i].concentracoes
            df.loc[i] = [h.latitude, h.longitude, h.comprimento, h.vazao, h.rugosidade_n, h.largura_rio, h.altitude,
                        h.inclinacao, h.ang_esquerdo, h.ang_direito, h.profundidade, h.velocidade, h.tensao_c, h.nivel_dagua,
                        h.froude, cf.temperatura, cf.k_2, cf.s_d, cf.k_d, cf.k_s, cf.l_rd, cf.k_so,
                        cf.k_oa, cf.k_an, cf.k_nn, cf.s_amon, cf.k_spo, cf.k_oi, cf.k_b, cf.r_o2_amon, cf.k_nit_od,
                        cc.conc_od, cc.conc_dbo, cc.conc_no, cc.conc_n_amon, cc.conc_nitrato, cc.conc_nitrito,
                        cc.conc_p_org, cc.conc_p_inorg, cc.conc_p_total, cc.conc_e_coli]
        lidt_df.append(df)
    
    return lidt_df, list_entr 


def plot_map(maps, df_new, colun, title, inverse_b):
    
    maps.add_trace(
        go.Scattermapbox(lon=df_new['lon'], lat=df_new['lat'], name=title,
                        marker={"autocolorscale": False,
                                "showscale":True, "size": 6, "opacity": 0.8,
                                "color": colun, "colorscale": 'haline',
                                "colorbar": dict(orientation='h')},
                        marker_reversescale=inverse_b))
    
    return


def plotar(n_tributarios, lista_modelagem, lidt_df, list_entr, labels, zona, hemisferio):
    
    from plotly.subplots import make_subplots

    list_tab = ['Gráficos do Rio Principal', 'Tabela Final']
    if str(lidt_df[0]['latitude'][0]) != 'nan':
        list_tab.append('Representação espacial')

    result_tabs = st.tabs(list_tab)

    with result_tabs[0]:
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

            if str(list_entr[0 + 1].descricao) == 'nan':

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
        for r in range(n_tributarios + 1):
            ex = st.expander('Dados do ' + labels[r])
            ex.write(lidt_df[r])

    if str(lidt_df[0]['latitude'][0]) != 'nan':
        with result_tabs[2]:       

            from pyproj import Proj
            
            df_new = pd.concat(lidt_df)
            myProj = Proj('+proj=utm +zone=' + str(zona)
                        + ' +' + str(hemisferio) + ' +ellps=WGS84',
                        preserve_units=False)
            df_new['lon'], df_new['lat'] = myProj(df_new['longitude'].values,
                                                  df_new['latitude'].values,
                                                  inverse=True)
            
            
            maps = go.Figure()

            maps.update_layout(title_text='Concentrações', title_font_color="teal",
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

