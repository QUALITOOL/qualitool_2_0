import streamlit as st
import pandas as pd
import numpy as np
import copy


def inicio(paramentro):
    
    st.divider()
    dados_anterior = st.checkbox("Preenchimento automático.")
    data = False
    if dados_anterior:
        uploaded_json = st.file_uploader("Submeter o arquivo 'DadosEntrada.json'"
                                         + " construído anteriormente:",
                                         type=["json"])
        if uploaded_json is not None:
            from json import load
            data_dict = load(uploaded_json)
            data = data_dict['dados'][0]
            paramentro = data['Paramêtros']
        else:
            st.markdown("""❗ Obs.: Evite alterar o arquivo 'DadosEntrada.json'
             utilizando o Excel. Se os dados não preencherem automaticamente,
             recomenda-se preencher de forma manual novamente.""")
    else:
        st.warning('''Se for a sua primeira vez no Qualitool 2.0,
                      você terá que preencher os dados de forma manual.''',
                      icon="❕")
    st.divider()
    
    col_1, col_2 = st.columns(2)
    bar = st.sidebar
    bar.warning('''Atenção! Em caso de atualização da tela, os dados 
                já preenchidos serão perdidos e precisarão ser 
                inseridos novamente.''',
                  icon="⚠️")

    col_1.markdown('Qual(s) parâmetro(s) modelar?')
    col_1_1, col_1_2 = col_1.columns(2)
    disab = False
    if data != False:
        disab = True
    modelar_od = col_1_1.checkbox('OD', value=paramentro[0], disabled=disab)
    modelar_dbo = col_1_1.checkbox('DBO', value=paramentro[2], disabled=disab)
    modelar_n = col_1_1.checkbox('Nitrogênio', value=paramentro[3], disabled=disab)
    modelar_p = col_1_2.checkbox('Fósforo', value=paramentro[4], disabled=disab)
    modelar_colif = col_1_2.checkbox('Coliformes', value=paramentro[5], disabled=disab)

    col_2.markdown('Configurações gerais:')
    serie_tempo = col_2.toggle('Ativar avaliação temporal.', value=paramentro[7], disabled=disab)
    if modelar_od:
            modelar_k_2 = col_2.toggle('Coeficiente k2 será tabelado.', value=paramentro[1], disabled=disab)
    else:
        modelar_k_2 = False

    n_tributarios = col_2.number_input(
        'Quantidade de tributários modeláveis:', min_value=0,
        value=paramentro[6], disabled=disab)
    
    
    lista_modelagem = [modelar_od, modelar_k_2, modelar_dbo, modelar_n,
                       modelar_p, modelar_colif, n_tributarios, serie_tempo]

    lista_tabs = ["tab0"]
    labels = ["Rio principal"]
    for n_trib in range(n_tributarios):
        lista_tabs.append("tab" + str(n_trib))
        labels.append("Tributário " + str(n_trib + 1))
    lista_tabs = st.tabs(labels)

    return (lista_modelagem, data, labels, lista_tabs)

######################### DADOS INICIAIS ##########################
def dados_iniciais(data, lista_modelagem, n_tributarios, labels, lista_tabs):
    # DADOS DE ENTRADA INICIAIS
    ponto_af = []
    list_desague = []
    list_valor_i = []
    list_discretizacao = []
    list_comprimento = []
    list_longitude = []
    list_latitude = []
    list_altitude = []
    list_secaotrav = []
    list_qnt_secaotrav = []
    zona = None
    hemisferio = None
    id_hmf = 0

    
    list_name_hid = ['Latitude (UTM)',
                    'Longitude (UTM)',
                    'Comprimento (m)',
                    'Rugosidade (manning)',
                    'Largura (m)',
                    'Ângulo esquerdo (°)',
                    'Ângulo direito (°)']
    list_valores_hid = [None, None, 0.0, 0.0, 0.0, 0.0, 0.0]

    for i in range(n_tributarios + 1):
        
        # DADOS PARA AUTOMATIZAÇÃO NA ENTRADA
        dis_i = 50.0
        qt_st = 0
        disab = False
        if data != False:
            dis_i = data['Dados gerais'][6][i]
            disab = True
            qt_st = data['Dados gerais'][7][i]

        comprimento = []
        longitude = []
        latitude = []
        altitude = []
        preecheu = False
        expander = lista_tabs[i].expander(
            "**:orange[DADOS DE ENTRADA INICIAIS]**")
        
        if i > 0:
            coll1, coll2 = expander.columns(2)
            labels_mod = copy.deepcopy(labels)
            labels_mod.remove(labels[i])

            if data != False:
                af_valor = data['Dados gerais'][8][i - 1]
                dt_desague = data['Dados gerais'][9][i - 1] - 1
                dt_desague = 0 if dt_desague < 0 else dt_desague
            else:
                af_valor = [0.0, None, None, None]
                dt_desague = 0
            desague = coll1.selectbox(str(i) + '. Deságua no:', labels_mod, index=dt_desague)
            coll2.markdown("Ponto de deságue em relação o " + desague + ":")

            df_afl = pd.DataFrame({
                str(i) + '. Descrição': ['ID (opcional)', 'Latitude (UTM)', 'Longitude (UTM)', 'Comprimento (m)'],
                'Valores': af_valor})
            df_afl_f = coll2.data_editor(df_afl, disabled=[str(i) + '. Descrição'])
            ponto_af.append(list(df_afl_f['Valores']))
            list_desague.append(labels.index(desague))
            
            expander.divider()

        col_11, col_12 = expander.columns(2)
        _, col_122 = col_12.columns(2)
        discret = col_122.number_input(
            str(i) + '. Discretização (m)', value=dis_i,
            min_value=0.1, step=1e-2, format="%.2f")
        
        tipo_entrada = col_11.radio(str(i) + ". Tipo de entrada dos dados espaciais:",
                                    ["Manual", "Intervalo","GeoJSON"],
                                    horizontal=True)
        df_esp = pd.DataFrame(columns=[str(i) + '. Latitude (UTM)', str(i) + '. Longitude (UTM)',
                                        str(i) + '. Altitude (m)', str(i) + '. Comprimento (m)'])

        if tipo_entrada == "Intervalo":
            col0_1, col0_2 = expander.columns(2)

            comp = col0_1.number_input(
                'Comprimento do ' + str(labels[i]) + ' (m)'
                + ' *a ser modelado*',
                min_value=150.0, step=1e-2, format="%.2f")
            
            col1_1, col1_2 = col0_2.columns(2)
            
            altit = col1_1.number_input(
                str(i) + '. Altitude inicial (m)', value=50.0,
                min_value=1.0, step=1e-2, format="%.2f")
            
            incl = col1_2.number_input(
                str(i) + '. Inclinação (m/m)',
                min_value=0.0001, step=1e-4, format="%.4f")


        if tipo_entrada == "Manual":
            
            if data != False:
                df_esp[str(i) + '. Latitude (UTM)'] = data['Dados gerais'][3][i]
                df_esp[str(i) + '. Longitude (UTM)'] = data['Dados gerais'][2][i]
                df_esp[str(i) + '. Altitude (m)'] = data['Dados gerais'][4][i]
                df_esp[str(i) + '. Comprimento (m)'] = data['Dados gerais'][1][i]

            expander.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                    icon="❕")
            df_espacial = expander.data_editor(df_esp,
                                               num_rows="dynamic",
                                               column_config={
                                                   str(i) + '. Latitude (UTM)':st.column_config.NumberColumn(format="%.2f"),
                                                   str(i) + '. Longitude (UTM)':st.column_config.NumberColumn(format="%.2f"),
                                                   str(i) + '. Altitude (m)':st.column_config.NumberColumn(format="%.2f"),
                                                   str(i) + '. Comprimento (m)':st.column_config.NumberColumn(format="%.2f")})
                
            if len(df_espacial[str(i) + '. Latitude (UTM)']) > 1:
                latitude = list(df_espacial.iloc[:,0])
                longitude = list(df_espacial.iloc[:,1])
                altitude = list(df_espacial.iloc[:,2])
                comprimento = list(df_espacial.iloc[:,3])
                if df_espacial[str(i) + '. Latitude (UTM)'][0] != None:
                    preecheu = True


        if tipo_entrada == "GeoJSON":
            df_espacial = expander.file_uploader(str(i) +
                                                ". ⚠️ Submeter o arquivo .GeoJSON, em WGS 84 UTM," +
                                                " contendo somente a coluna 'Altitude' em metros.",
                                                type=["geojson"])
            
            if df_espacial is not None:
                from geopandas import read_file
                gdf = read_file(df_espacial)
                preecheu = True
                for x in range(len(gdf)):
                    longitude.append(gdf["geometry"][x].x)
                    latitude.append(gdf["geometry"][x].y)

                altitude = list(gdf.iloc[:,1])
                comprimento = []
                for ct in range(len(altitude)):
                    comprimento.append(None)
        if preecheu:
            col1, col2 = expander.columns(2)
            coln1, coln2 = col1.columns(2)
            if data != False:
                id_hmf = data['Dados gerais'][11]
                zona_dt = data['Dados gerais'][10]

            else:
                zona_dt = 22
            zona = coln1.number_input(
                str(i) + '. WGS 84 - UTM - Zona:', min_value=0, value=zona_dt)
            hemisferio = coln2.radio(str(i) + '. Hemisfério:', ['Sul', 'Norte'],
                                    horizontal=True, index=id_hmf)
            if hemisferio == 'Sul':
                hemisferio = 'south'
                id_hmf = 0
            else:
                hemisferio = 'north'
                id_hmf = 1
            on = col2.toggle(str(i) + '. Visualizar dados espaciais')
        
            if on:

                from pyproj import Proj

                df_plot = pd.DataFrame({'UTMlon': longitude, 'UTMlat': latitude})
                myProj = Proj('+proj=utm +zone=' + str(zona)
                            + ' +' + str(hemisferio) + ' +ellps=WGS84',
                            preserve_units=False)
                df_plot['lon'], df_plot['lat'] = myProj(df_plot['UTMlon'].values,
                                                        df_plot['UTMlat'].values,
                                                        inverse=True)
                expander.map(df_plot, size = 1, color='#007FFF')

        else:       
            if tipo_entrada == "Intervalo":
                comprimento = list(np.arange(0, comp + discret, discret))
                
                for k in range(len(comprimento)):
                    altitude.append(altit - (discret * incl))
                    latitude.append(None)
                    longitude.append(None)

        expander.divider()

        expander.markdown(":orange[Variáveis iniciais do " + str(labels[i]) + ":]")


        ############################################
        if lista_modelagem[7]:
            list_name = ['Data',str(i) + '. Q (m³/s)']
            list_valores = [None, [0.0]] 
        else:
            list_name = [str(i) + '. Q (m³/s)']
            list_valores = [[0.0]] 

        if lista_modelagem[0]:
            list_name.extend(['OD (mg/L)',
                                'DBO (mg/L)'])
            list_valores.extend([[0.0], [0.0]])
        if lista_modelagem[3]:
            list_name.extend(['N-org (mg/L)',
                                'N-amon (mg/L)',
                                'N-nitri (mg/L)',
                                'N-nitra (mg/L)'])
            list_valores.extend([[0.0], [0.0], [0.0], [0.0]])
        if lista_modelagem[4]:
            list_name.extend(['P-org (mg/L)',
                                'P-inorg (mg/L)'])
            list_valores.extend([[0.0], [0.0]])
        if lista_modelagem[5]:
            list_name.append('E-coli (NMP/100ml)')
            list_valores.extend([[0.0]])
        colmdisab = None
        if data != False:
            colmdisab = 'Data'
            list_valores = data['Dados gerais'][0][i]
            if lista_modelagem[7]:
                list_valores[0] = pd.to_datetime(list_valores[0])

        if lista_modelagem[7]:
            num_rows = "dynamic"
        else:
            num_rows = "fixed"
        df_conc = pd.DataFrame(columns=list_name)

        if i == 0:
            valores = copy.deepcopy(list_valores)
            for y in range(len(list_name)):
                df_conc[list_name[y]] = list_valores[y]
            df_conc_f = expander.data_editor(df_conc, num_rows=num_rows,
                                            column_config={
                                                'Data':st.column_config.DateColumn(
                                                    format="MM.DD.YYYY", step=1),
                                                },
                                            disabled=[colmdisab])
            dias = list(df_conc_f[list_name[0]])
            
        else:
            valores2 = copy.deepcopy(valores)
            valores2.pop(0)
            if lista_modelagem[7] and data == False:
                l_valor = []
                for id in range(len(valores2)):
                    l_valor.append(valores2[id][0])
                for id2 in range(len(dias)):
                    soma = [dias[id2]] + l_valor
                    df_conc.loc[id2] = soma
            
            else:
                for y in range(len(list_name)):
                    df_conc[list_name[y]] = list_valores[y]

            df_conc_f = expander.data_editor(df_conc,
                                            column_config={
                                                'Data':st.column_config.DateColumn(
                                                    format="MM.DD.YYYY", step=1),
                                                },
                                            disabled=['Data'])
        
        list_valores_f = []
        for yf in range(len(list_name)):
            lista = list(df_conc_f[list_name[yf]])
            if yf == 0  and lista_modelagem[7] and df_conc_f[list_name[yf]][0] != None and data != False:
                list_valores_f.append(list(df_conc_f[list_name[yf]].dt.strftime('%Y %m %d')))

            else:
                list_valores_f.append(lista)
    

        expander.divider()
        expander.markdown(":orange[Seções transversais do " + str(labels[i]) + ":]")
        col_3_1, _ = expander.columns(2)
        n_pontos_st = col_3_1.number_input(
            str(i) + '. Quantidade de pontos que alteram os valores'
            + ' de uma ou mais variáveis hidráulicas:',
            min_value=0, value= qt_st, disabled=disab)
        df_hid = pd.DataFrame({str(i) + '. Descrição': list_name_hid})
        for k in range(n_pontos_st + 1):
            if data != False:
                df_hid['Ponto ' + str(k)] = data['Dados gerais'][5][i][k]

            else:
                df_hid['Ponto ' + str(k)] = list_valores_hid
        df_hid_f = expander.data_editor(df_hid, disabled=[str(i) + '. Descrição'])
        hidr = []
        for k in range(n_pontos_st + 1):
            hidr.append(list(df_hid_f['Ponto ' + str(k)]))


        
        list_comprimento.append(comprimento)
        list_longitude.append(longitude)
        list_latitude.append(latitude)
        list_altitude.append(altitude)
        list_discretizacao.append(discret)
        list_valor_i.append(list_valores_f)
        list_secaotrav.append(hidr)
        list_qnt_secaotrav.append(n_pontos_st)

    lista_parametros = [list_valor_i, list_comprimento, list_longitude,
                        list_latitude, list_altitude, list_secaotrav,
                        list_discretizacao, list_qnt_secaotrav, ponto_af,
                        list_desague, zona, id_hmf]
    
    return lista_parametros, list_name, valores, zona, hemisferio, dias


########################## COEFICIENTES ###########################
def coeficientes(data, lista_modelagem, n_tributarios, labels, lista_tabs, dias):
    # COEFICIENTES DDO MODEDELO
    list_name = ['Temperatura (°C)']
    if lista_modelagem[1]:
        list_name.append('k2 (1/d)')
    if lista_modelagem[0]:
        list_name.extend(['k1 (1/d)',
                          'kd (1/d)',
                          'ks (1/d)',
                          'lrd (gDBO5/m.d)',
                          'sd (1/d)'])
    if lista_modelagem[0] == True and lista_modelagem[3] == True:
        list_name.append('O2namon (mgO2/mgNamon oxid)')
    if lista_modelagem[3]:
        list_name.extend(['koa (1/d)',
                          'kso (1/d)',
                          'kan (1/d)',
                          'Snamon (g/m2.d)',
                          'knn (1/d)',
                          'knitr (1/d)'])
    if lista_modelagem[4]:
        list_name.extend(['koi (1/d)',
                            'kspo (1/d)',
                            'spinorg (1/d)'])
    if lista_modelagem[5]:
        list_name.append('kb (1/d)')

    lista_coeficiente = [list_name]
    lista_n_pontos = []

    for i in range(n_tributarios + 1):
        list_name_c = ['Latitude (UTM)',
                    'Longitude (UTM)',
                    'Comprimento (m)']
        list_valores_c = [None, None, 0.0]
        if lista_modelagem[1] == False and lista_modelagem[0] == True:
            list_name_c.append('k2 máximo (1/d)')
            list_valores_c.append(1000.0)

        expander = lista_tabs[i].expander(
            "**:green[COEFICIENTES DO MODELO]**")
        col_11, col_21 = expander.columns(2)

        qt_coe = 0
        disab = False
        if data != False:
            qt_coe = data['Coeficientes'][1][i]
            disab = True

        col_21.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                             icon="❕")

        expander.markdown(":green[Variáveis do " + str(labels[i]) +":]")
        coef = []
        
        n_pontos = col_11.number_input(
            str(i) + '. Quantidade de ponto que alteram os valores'
            + ' de um ou mais coeficientes tabelados:',
            min_value=0, value=qt_coe, disabled=disab)
        lista_n_pontos.append(n_pontos)
        df_coef = pd.DataFrame({str(i) + '. Descrição': list_name_c})
        labels_c = []  
        for k in range(n_pontos + 1):
            labels_c.append(str(i) + '. Ponto ' + str(k))
            if data != False:
                df_coef['Ponto ' + str(k)] = data['Coeficientes'][0][i+1][0][k]

            else:
                df_coef['Ponto ' + str(k)] = list_valores_c
        df_coef_f = expander.data_editor(df_coef, disabled=[str(i) + '. Descrição'])


        tabs_c = expander.tabs(labels_c)
        for tc in range(len(labels_c)):
            if lista_modelagem[7]:
                list_name_c2 = ['Data', str(i) + '.' + str(tc) +'. Temperatura (°C)']
            else:
                list_name_c2 = [str(i) + '.' + str(tc) +'. Temperatura (°C)']
            list_valores_c2 = [[22.0]]
            if lista_modelagem[1]:
                list_name_c2.append('k2 (1/d)')
                list_valores_c2.append([0.0])
            if lista_modelagem[0]:
                list_name_c2.extend(['k1 (1/d)',
                                'kd (1/d)',
                                'ks (1/d)',
                                'lrd (gDBO5/m.d)',
                                'sd (1/d)'])
                list_valores_c2.extend([[0.0], [0.0], [0.0], [0.0], [0.0]])
            if lista_modelagem[0] == True and lista_modelagem[3] == True:
                list_name_c2.append('O2namon (mgO2/mgNamon oxid)')
                list_valores_c2.append([0.0])
            if lista_modelagem[3]:
                list_name_c2.extend(['koa (1/d)',
                                'kso (1/d)',
                                'kan (1/d)',
                                'Snamon (g/m2.d)',
                                'knn (1/d)',
                                'knitr (1/d)'])
                list_valores_c2.extend([[0.0], [0.0], [0.0], [0.0], [0.0], [0.0]])
            if lista_modelagem[4]:
                list_name_c2.extend(['koi (1/d)',
                                    'kspo (1/d)',
                                    'spinorg (1/d)'])
                list_valores_c2.extend([[0.0], [0.0], [0.0]])
            if lista_modelagem[5]:
                list_name_c2.append('kb (1/d)')
                list_valores_c2.append([0.0])
        
            df_coef2 = pd.DataFrame(columns=list_name_c2)

            if data != False:
                list_valores_c2 = data['Coeficientes'][0][i+1][tc][1]

            if lista_modelagem[7] and data == False:
                l_valor_c = []
                for id in range(len(list_valores_c2)):
                    l_valor_c.append(list_valores_c2[id][0])
                for id2 in range(len(dias)):
                    soma = [dias[id2]] + l_valor_c
                    df_coef2.loc[id2] = soma
            
            else:
                for yc in range(len(list_name_c2)):
                    if lista_modelagem[7] == True:
                        if yc == 0:
                            df_coef2[list_name_c2[yc]] = dias
                        else:
                            df_coef2[list_name_c2[yc]] = list_valores_c2[yc - 1]
                    else:
                        df_coef2[list_name_c2[yc]] = list_valores_c2[yc]

            df_coef2_f = tabs_c[tc].data_editor(df_coef2,
                                            column_config={
                                                'Data':st.column_config.DateColumn(
                                                    format="MM.DD.YYYY", step=1),
                                                },
                                            disabled=['Data'])
            list_valores_c2 = []
            for yf in range(len(list_name_c2)):
                if yf == 0 and lista_modelagem[7] == True:
                    pass
                else:
                    list_valores_c2.append(list(df_coef2_f[list_name_c2[yf]]))
            list_c1 = []

            for c1 in list(df_coef_f['Ponto ' + str(tc)]):
                if c1 != None:
                    list_c1.append(float(c1))
                else:
                    list_c1.append(c1)

            coef.append([list_c1, list_valores_c2])

        lista_coeficiente.append(coef)
    list_coef_f = [lista_coeficiente, lista_n_pontos]
    return list_coef_f


################### RETIRADAS E CONTRIBUIÇÕES #####################
def fun_contrib_retirad(data, n_tributarios, labels, lista_tabs, list_name, list_valores, lista_modelagem, dias):

    list_name_cr = ['ID (opcional)',
                    'Latitude (UTM)',
                    'Longitude (UTM)',
                    'Comprimento (m)']
    list_valores_cr = [None, None, None, 0.0]
    list_name.pop(0)
    list_valores.pop(0)
    if lista_modelagem[7]:
        list_name.pop(0)
        list_valores.pop(0)


    list_retiradas = []
    list_ep = []
    list_ed = []
    list_qnt = []

    for j in range(n_tributarios + 1):
        
        expander = lista_tabs[j].expander("**:blue[CONTRIBUIÇÕES E RETIRADAS]**")

        qt_ret = 1
        on_ret = False
        qt_ep = 1
        on_ep = False
        qt_ed = 1
        on_ed = False
        disab = False
        if data != False:
            qt_ret = data['Contr e Retir'][3][j][0]
            qt_ep = data['Contr e Retir'][3][j][1]
            qt_ed = data['Contr e Retir'][3][j][2]
            on_ret = data['Contr e Retir'][3][j][3]
            on_ep = data['Contr e Retir'][3][j][4]
            on_ed = data['Contr e Retir'][3][j][5]
            disab = True

        retiradas = expander.checkbox(str(j) + '. Possui algum ponto de **captação de água**.',
                                          value=on_ret, disabled=disab)
        ret = []
        n_pontos_r = 0
        if retiradas:
            col4_1, col4_2 = expander.columns(2)
            col4_1.markdown(":blue[Retiradas do " + str(labels[j]) + ":]")
            col4_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                           icon="❕")
            n_pontos_r = col4_1.number_input(
                str(j) + '. Quantidade de ponto de captação:',
                min_value=1, value=qt_ret, disabled=disab)
            dfret = pd.DataFrame({str(j) + '. R: Variável': list_name_cr})
            labels_r = []
            for k in range(n_pontos_r):
                labels_r.append(str(j) + '. Ponto ' + str(k))
                if data != False:
                    dfret['Ponto ' + str(k)] = data['Contr e Retir'][0][j][0][k]

                else:
                    dfret['Ponto ' + str(k)] = list_valores_cr
            df_ret_f = expander.data_editor(dfret, disabled=[str(j) + '. R: Variável'])


            tabs_r = expander.tabs(labels_r)
            for tr in range(len(labels_r)):
                if lista_modelagem[7]:
                    list_name_r = ['Data', str(j) + '.' + str(tr) +'. Q (m³/s)']
                else:
                    list_name_r = [str(j) + '.' + str(tr) +'. Q (m³/s)']
                    
                list_valores_r = [[0.0]]
                df_ret2 = pd.DataFrame(columns=list_name_r)

                if data != False:
                    list_valores_r = data['Contr e Retir'][1][j][tr][1]

                if lista_modelagem[7] and data == False:
                    l_valor_r = []
                    for id in range(len(list_valores_r)):
                        l_valor_r.append(list_valores_r[id][0])
                    for id2 in range(len(dias)):
                        soma = [dias[id2]] + l_valor_r
                        df_ret2.loc[id2] = soma
                
                else:
                    for yc in range(len(list_name_r)):
                        if lista_modelagem[7] == True:
                            if yc == 0:
                                df_ret2[list_name_r[yc]] = dias
                            else:
                                df_ret2[list_name_r[yc]] = list_valores_r[yc - 1]
                        else:
                            df_ret2[list_name_r[yc]] = list_valores_r[yc]

                df_ret2_f = tabs_r[tr].data_editor(df_ret2,
                                                   column_config={
                                                       'Data':st.column_config.DateColumn(
                                                           format="MM.DD.YYYY", step=1),
                                                           },
                                                   disabled=['Data'])
                list_valores_r = []
                for rf in range(len(list_name_r)):
                    if rf == 0 and lista_modelagem[7] == True:
                        pass
                    else:
                        list_valores_r.append(list(df_ret2_f[list_name_r[rf]]))    

                ret.append([list(df_ret_f['Ponto ' + str(tr)]), list_valores_r])


        expander.divider()
        contr_pontual = expander.checkbox(str(j) + '. Possui algum ponto de **descarga de poluição pontual**.',
                                          value=on_ep, disabled=disab)
        ep = []
        n_pontos_ep = 0
        if contr_pontual:
            col4_1, col4_2 = expander.columns(2)
            col4_1.markdown(":blue[Contribuições pontuais do " + str(labels[j]) + ":]")
            col4_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                           icon="❕")
            n_pontos_ep = col4_1.number_input(
                str(j) + '. Quantidade de pontos de entradas pontuais:',
                min_value=1, value=qt_ep, disabled=disab)
            dfep = pd.DataFrame({str(j) + '. EP: Variável': list_name_cr})
            labels_ep = []
            for k in range(n_pontos_ep):
                labels_ep.append(str(j) + '. Ponto ' + str(k))
                if data != False:
                    dfep['Ponto ' + str(k)] = data['Contr e Retir'][1][j][0][k]

                else:
                    dfep['Ponto ' + str(k)] = list_valores_cr
            df_ep_f = expander.data_editor(dfep, disabled=[str(j) + '. EP: Variável'])


            tabs_ep = expander.tabs(labels_ep)
            for tep in range(len(labels_ep)):
                if lista_modelagem[7]:
                    list_name_ep = ['Data', str(j) + '.' + str(tep) +'. Q (m³/s)'] + list_name
                else:
                    list_name_ep = [str(j) + '.' + str(tep) +'. Q (m³/s)'] + list_name
                
                list_valores_ep = [[0.0]] + list_valores
                df_ep2 = pd.DataFrame(columns=list_name_ep)

                if data != False:
                    list_valores_ep = data['Contr e Retir'][1][j][tep][1]

                if lista_modelagem[7] and data == False:
                    l_valor = []
                    for id in range(len(list_valores_ep)):
                        l_valor.append(list_valores_ep[id][0])
                    for id2 in range(len(dias)):
                        soma = [dias[id2]] + l_valor
                        df_ep2.loc[id2] = soma
                
                else:
                    for yc in range(len(list_name_ep)):
                        if lista_modelagem[7] == True:
                            if yc == 0:
                                df_ep2[list_name_ep[yc]] = dias
                            else:
                                df_ep2[list_name_ep[yc]] = list_valores_ep[yc - 1]
                        else:
                            df_ep2[list_name_ep[yc]] = list_valores_ep[yc]


                df_ep2_f = tabs_ep[tep].data_editor(df_ep2, 
                                                   column_config={
                                                       'Data':st.column_config.DateColumn(
                                                           format="MM.DD.YYYY", step=1),
                                                           },
                                                   disabled=['Data'])
                list_valores_ep = []
                for epf in range(len(list_name_ep)):
                    if epf == 0 and lista_modelagem[7] == True:
                        pass
                    else:
                        list_valores_ep.append(list(df_ep2_f[list_name_ep[epf]]))    

                ep.append([list(df_ep_f['Ponto ' + str(tep)]), list_valores_ep])


        expander.divider()
        contr_difusa = expander.checkbox(str(j) + '. Possui algum ponto de **descarga de poluição difusa**.',
                                          value=on_ed, disabled=disab)
        ed = []
        n_pontos_ed = 0
        if contr_difusa:
            col4_1, col4_2 = expander.columns(2)
            col4_1.markdown(":blue[Contribuições difusa do " + str(labels[j]) + ":]")
            col4_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                           icon="❕")
            n_pontos_ed = col4_1.number_input(
                str(j) + '. Quantidade de pontos de entradas difusas:',
                min_value=1, value=qt_ed, disabled=disab)
            list_name_ed = ['ID (opcional)',
                            'Latitude inicial (UTM)',
                            'Latitude final (UTM)',
                            'Longitude inicial (UTM)',
                            'Longitude final (UTM)',
                            'Comprimento inicial (m)',
                            'Comprimento final (m)']
            list_valores_ed = [None, None, None, None, None, 0.0, 0.0]
            dfed = pd.DataFrame({str(j) + '. ED: Variável': list_name_ed})
            labels_ed = []
            for k in range(n_pontos_ed):
                labels_ed.append(str(j) + '. Ponto ' + str(k))
                if data != False:
                    dfed['Ponto ' + str(k)] = data['Contr e Retir'][2][j][0][k]

                else:
                    dfed['Ponto ' + str(k)] = list_valores_ed
            df_ed_f = expander.data_editor(dfed, disabled=[str(j) + '. ED: Variável'])


            tabs_ed = expander.tabs(labels_ed)
            for ted in range(len(labels_ed)):
                if lista_modelagem[7]:
                    list_name_ed = ['Data', str(j) + '.' + str(ted) +'. Q TOTAL (m³/s)'] + list_name
                else:
                    list_name_ed = [str(j) + '.' + str(ted) +'. Q TOTAL (m³/s)'] + list_name

                list_valores_ed = [[0.0]] + list_valores
                df_ed2 = pd.DataFrame(columns=list_name_ed)

                if data != False:
                    list_valores_ed = data['Contr e Retir'][2][j][ted][1]

                if lista_modelagem[7] and data == False:
                    l_valor_ed = []
                    for id in range(len(list_valores_ed)):
                        l_valor_ed.append(list_valores_ed[id][0])
                    for id2 in range(len(dias)):
                        soma = [dias[id2]] + l_valor_ed
                        df_ed2.loc[id2] = soma
                
                else:
                    for yc in range(len(list_name_ed)):
                        if lista_modelagem[7] == True:
                            if yc == 0:
                                df_ed2[list_name_ed[yc]] = dias
                            else:
                                df_ed2[list_name_ed[yc]] = list_valores_ed[yc - 1]
                        else:
                            df_ed2[list_name_ed[yc]] = list_valores_ed[yc]
                

                df_ed2_f = tabs_ed[ted].data_editor(df_ed2,
                                                   column_config={
                                                       'Data':st.column_config.DateColumn(
                                                           format="MM.DD.YYYY", step=1),
                                                           },
                                                   disabled=['Data'])
                list_valores_ed = []
                for edf in range(len(list_name_ed)):
                    if edf == 0 and lista_modelagem[7] == True:
                        pass
                    else:
                        list_valores_ed.append(list(df_ed2_f[list_name_ed[edf]]))    

                ed.append([list(df_ed_f['Ponto ' + str(ted)]), list_valores_ed])

        expander.divider()
        list_retiradas.append(ret)
        list_ep.append(ep)
        list_ed.append(ed)
        list_qnt.append([n_pontos_r, n_pontos_ep, n_pontos_ed,
                         retiradas, contr_pontual, contr_difusa])
    
    lista_contr_retir = [list_retiradas, list_ep, list_ed, list_qnt]

    return lista_contr_retir


####################### SALVAR ARQUIVO JSON #######################
def salvararquivo(lista_modelagem, lista_parametros, lista_coeficiente, lista_contr_retir,
                  list_name_salvo, list_valores):
    col_1, col_2 = st.columns(2)
    salvar = col_2.toggle('Salvar dados preenchidos.')
    if salvar:
        data = {'dados': [{'Paramêtros': lista_modelagem, 'Dados gerais': lista_parametros,
                'Coeficientes': lista_coeficiente, 'Contr e Retir': lista_contr_retir,
                'Nomes': list_name_salvo, 'Valores': list_valores}]}
        from json import dumps
        json_string = dumps(data)

        col_1.download_button(
            label="Clique para fazer o Download",
            file_name="DadosEntrada.json",
            mime="application/json",
            data=json_string,
        )
    return

