import streamlit as st
import pandas as pd
import numpy as np



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
    col_2.warning('''Atenção! Caso a tela atualize os dados já preenchidos
                  serão pertidos e devão ser preenchidos novamente.''',
                  icon="⚠️")

    col_1.markdown('Qual(s) parâmetro(s) modelar?')
    col_1_1, col_1_2 = col_1.columns(2)
    disab = False
    if data != False:
        disab = True
    modelar_od = col_1_1.checkbox('OD', value=paramentro[0], disabled=disab)
    if modelar_od:
            modelar_k_2 = col_1_1.checkbox('k2 tabelado', value=paramentro[1], disabled=disab)
    else:
        modelar_k_2 = False
    modelar_dbo = col_1_1.checkbox('DBO', value=paramentro[2], disabled=disab)
    modelar_n = col_1_2.checkbox('Nitrogênio', value=paramentro[3], disabled=disab)
    modelar_p = col_1_2.checkbox('Fósforo', value=paramentro[4], disabled=disab)
    modelar_colif = col_1_2.checkbox('Coliformes', value=paramentro[5], disabled=disab)
    n_tributarios = col_2.number_input(
        'Quantidade de tributários modeláveis:', min_value=0,
        value=paramentro[6], disabled=disab)
    lista_modelagem = [modelar_od, modelar_k_2, modelar_dbo, modelar_n,
                       modelar_p, modelar_colif, n_tributarios]

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

    
    list_name_hid = ['Latitude (UTM)',
                    'Longitude (UTM)',
                    'Comprimento (m)',
                    'Rugosidade (manning)',
                    'Largura (m)',
                    'Ângulo esquerdo (°)',
                    'Ângulo direito (°)']
    list_valores_hid = [None, None, None, 0.0, 0.0, 0.0, 0.0]

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
        col_11, col_12 = expander.columns(2)
        col_121, col_122 = col_12.columns(2)
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

        expander.divider()
        col1, col2 = expander.columns(2)


        if i > 0:
            col1.markdown(":orange[Ponto em relação ao " + str(labels[0]) + ":]")
            if data != False:
                af_valor = data['Dados gerais'][8][i - 1]
            else:
                af_valor = [0.0, None, None, None]
            df_afl = pd.DataFrame({
                str(i) + '. Descrição': ['ID (opcional)', 'Latitude (UTM)', 'Longitude (UTM)', 'Comprimento (m)'],
                'Valores': af_valor})
            df_afl_f = col1.data_editor(df_afl, disabled=[str(i) + '. Descrição'])
            ponto_af.append(list(df_afl_f['Valores']))



        col1.markdown(":orange[Variáveis iniciais do " + str(labels[i]) + ":]")
        if data != False:
            list_name = data['Nomes']
            list_valores = data['Dados gerais'][0][i]

        ############################################
        else:
            list_name = ['Vazão (m³/s)']
            list_valores = [0]
            if lista_modelagem[0]:
                list_name.extend(['Oxigênio dissolvido (mg/L)',
                                    'DBO (mg/L)'])
                list_valores.extend([0.0, 0.0])
            if lista_modelagem[3]:
                list_name.extend(['Nitrogênio orgânico (mg/L)',
                                    'Amônia (mg/L)',
                                    'Nitrito (mg/L)'])
                list_valores.extend([0.0, 0.0, 0.0])
            if lista_modelagem[4]:
                list_name.extend(['Fósforo orgânico (mg/L)',
                                    'Fósforo inorgânico (mg/L)'])
                list_valores.extend([0.0, 0.0])
            if lista_modelagem[5]:
                list_name.append('E-coli (NMP/100ml)')
                list_valores.append(0.0)

        df_conc = pd.DataFrame({str(i) + '. Descrição': list_name, 'Valores': list_valores})
        df_conc_f = col1.data_editor(df_conc, disabled=[str(i) + '. Descrição'])
        if preecheu:
            coln1, coln2 = col2.columns(2)
            zona = coln1.number_input(
                str(i) + '. WGS 84 - UTM - Zona:', min_value=0, value=22)
            hemisferio = coln2.radio(str(i) + '. Hemisfério:', ['Sul', 'Norte'],
                                    horizontal=True)
            if hemisferio == 'Sul':
                hemisferio = 'south'
            else:
                hemisferio = 'north'
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
                col2.map(df_plot, size = 1, color='#007FFF')

        else:       
            if tipo_entrada == "Intervalo":
                comprimento = list(np.arange(0, comp + discret, discret))
                for k in range(len(comprimento)):
                    altitude.append(altit - (discret * incl))
                    latitude.append(None)
                    longitude.append(None)
    

        expander.divider()
        expander.markdown(":orange[Secções transversais do " + str(labels[i]) + ":]")
        col_3_1, col_3_2 = expander.columns(2)
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
        list_valor_i.append(list(df_conc_f['Valores']))
        list_secaotrav.append(hidr)
        list_qnt_secaotrav.append(n_pontos_st)

    lista_parametros = [list_valor_i, list_comprimento, list_longitude,
                        list_latitude, list_altitude, list_secaotrav,
                        list_discretizacao, list_qnt_secaotrav, ponto_af]
    return lista_parametros, list_name, list_valores, zona, hemisferio


########################## COEFICIENTES ###########################
def coeficientes(data, lista_modelagem, n_tributarios, labels, lista_tabs):
    # COEFICIENTES DDO MODEDELO

    lista_qnt_coef = []
    list_name = ['Latitude (UTM)',
                 'Longitude (UTM)',
                 'Comprimento (m)',
                 'Temperatura (°C)']
    list_valores = [None, None, None, 22.0]
    if lista_modelagem[1]:
        list_name.append('k2 (1/d)')
        list_valores.append(0.0)
    if lista_modelagem[1] == False and lista_modelagem[0] == True:
        list_name.append('k2 máximo (1/d)')
        list_valores.append(0.0)
    if lista_modelagem[0]:
        list_name.extend(['k1 (1/d)',
                          'kd (1/d)',
                          'ks (1/d)',
                          'lrd (gDBO5/m.d)',
                          'sd (1/d)'])
        list_valores.extend([0.0, 0.0, 0.0, 0.0, 0.0])
    if lista_modelagem[0] == True and lista_modelagem[3] == True:
        list_name.append('O2namon (mgO2/mgNamon oxid)')
        list_valores.append(0.0)
    if lista_modelagem[3]:
        list_name.extend(['koa (1/d)',
                          'kso (1/d)',
                          'kan (1/d)',
                          'Snamon (g/m2.d)',
                          'knn (1/d)',
                          'knitr (1/d)'])
        list_valores.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    if lista_modelagem[4]:
        list_name.extend(['koi (1/d)',
                            'kspo (1/d)',
                            'spinorg (1/d)'])
        list_valores.extend([0.0, 0.0, 0.0])
    if lista_modelagem[5]:
        list_name.append('kb (1/d)')
        list_valores.append(0.0)

    lista_coeficiente = [list_name]

    for i in range(n_tributarios + 1):
        expander = lista_tabs[i].expander(
            "**:green[COEFICIENTES DO MODELO]**")
        col_1, col_2 = expander.columns(2)

        qt_coe = 0
        disab = False
        if data != False:
            qt_coe = data['Coeficientes'][1][i]
            disab = True

        option = col_1.selectbox(
            str(i) + '. Tem dúvida do que significa cada variável?',
            (list_name),
            index=None,
            placeholder="Selecione o nome da variável...",)
        if option != None:
            with col_2.chat_message("human", avatar="ai"):
                if option == 'Latitude (UTM)':
                    st.write('''Latitude na projeção WGS 84 em coordenadas UTM.''')
                elif option == 'Longitude (UTM)':
                    st.write('''Longitude na projeção WGS 84 em coordenadas UTM.''')
                elif option == 'Comprimento (m)':
                    st.write('''Comprimento a partir do trecho inicial do rio, em metros.''')
                elif option == 'Temperatura (°C)':
                    st.write('''Temperatura do rio, em grau celsius.''')
                elif option == 'k1 (1/d)':
                    st.write('''Coeficiente de desoxigenação, na temperatura de 20°C.''')
                elif option == 'kd (1/d)':
                    st.write('''Coeficiente de decomposição de DBO, na temperatura de 20°C.''')
                elif option == 'ks (1/d)':
                    st.write('''Coeficiente de sedimentação de DBO, na temperatura de 20°C.''')
                elif option == 'lrd (gDBO5/m.d)':
                    st.write('''Carga linear distribuída ao longo do rio, na temperatura de 20°C.''')
                elif option == 'sd (1/d)':
                    st.write('''Taxa consumo de O2 por demanda do sedimento, na temperatura de 20°C.''')
                elif option == 'O2namon (mgO2/mgNamon oxid)':
                    st.write('''Relação entre o oxigênio consumido por cada unidade de 
                             amônia oxidada a nitrito, na temperatura de 20°C.''')
                elif option == 'koa (1/d)':
                    st.write('''Coeficiente de conversão do nitrogênio orgânico 
                             a amônia, na temperatura de 20°C.''')
                elif option == 'kso (1/d)':
                    st.write('''Coeficiente de sedimentação do nitrogênio 
                             orgânico, na temperatura de 20°C.''')
                elif option == 'kan (1/d)':
                    st.write('''Coeficiente de conversão da amônia a 
                             nitrito, na temperatura de 20°C.''')
                elif option == 'Snamon (g/m2.d)':
                    st.write('''Fluxo de liberação de amônia pelo 
                             sedimento de fundo, na temperatura de 20°C.''')
                elif option == 'knn (1/d)':
                    st.write('''Coeficiente de conversão do nitrito a nitrato
                             , na temperatura de 20°C.''')
                elif option == 'knitr (1/d)':
                    st.write('''Coeficiente de inibição da nitrificação por baixo OD, 
                             na temperatura de 20°C. \n Usado para o cálculo do Fator de
                             correção do coeficiente de nitrificação em função do OD.''')
                elif option == 'koi (1/d)':
                    st.write('''Coeficiente de conversão do fósforo orgânico a fósforo 
                             inorgânico, na temperatura de 20°C.''')
                elif option == 'kspo (1/d)':
                    st.write('''Coeficiente de sedimentação do fósforo orgânico
                             , na temperatura de 20°C.''')
                elif option == 'spinorg (1/d)':
                    st.write('''Fluxo de liberação de fósforo inorgânico pelo sedimento 
                             de fundo, na temperatura de 20°C.''')
                elif option == 'kb (1/d)':
                    st.write('''Coeficiente de decaimento de coliforme, na temperatura de 20°C.''')
                else:
                    st.text('''ERRO''')
        else:
            col_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                             icon="❕")
        expander.divider()
        expander.markdown(":green[Variáveis do " + str(labels[i]) +":]")
        col_11, col_21 = expander.columns(2)
        n_pontos = col_11.number_input(
            str(i) + '. Quantidade de ponto que alteram os valores'
            + ' de um ou mais coeficientes tabelados:',
            min_value=0, value=qt_coe, disabled=disab)
        df_coef = pd.DataFrame({str(i) + '. Descrição': list_name})        
        for k in range(n_pontos + 1):
            if data != False:
                df_coef['Ponto ' + str(k)] = data['Coeficientes'][0][i+1][k]

            else:
                df_coef['Ponto ' + str(k)] = list_valores
        df_coef_f = expander.data_editor(df_coef, disabled=[str(i) + '. Descrição'])
        coef = []
        for k in range(n_pontos + 1):
            coef.append(list(df_coef_f['Ponto ' + str(k)]))

        lista_coeficiente.append(coef)
        lista_qnt_coef.append(n_pontos)
    list_coef_f = [lista_coeficiente, lista_qnt_coef]
    return list_coef_f


################### RETIRADAS E CONTRIBUIÇÕES #####################
def fun_contrib_retirad(data, n_tributarios, labels, lista_tabs, list_name, list_valores):

    list_name_cr = ['ID (opcional)',
                    'Latitude (UTM)',
                    'Longitude (UTM)',
                    'Comprimento (m)']
    list_valores_cr = [None, None, None, None]

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
            list_name_ret = list_name_cr + ['Vazão (m³/s)']
            list_valores_ret = list_valores_cr  + [0.0]
            dfret = pd.DataFrame({str(j) + '. Variável': list_name_ret})
            for k in range(n_pontos_r):
                if data != False:
                    dfret['Ponto ' + str(k)] = data['Contr e Retir'][0][j][k]

                else:
                    dfret['Ponto ' + str(k)] = list_valores_ret
            df_ret_f = expander.data_editor(dfret, disabled=[str(j) + '. Variável'])
            for n in range(n_pontos_r):
                ret.append(list(df_ret_f['Ponto ' + str(n)]))


        expander.divider()
        contr_pontual = expander.checkbox(str(j) + '. Possui algum ponto de **contribuição pontual**.',
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
            list_name_ep = list_name_cr + list_name
            list_valores_ep = list_valores_cr  + list_valores
            dfep = pd.DataFrame({str(j) + '. Variável': list_name_ep})
            for k in range(n_pontos_ep):
                if data != False:
                    dfep['Ponto ' + str(k)] = data['Contr e Retir'][1][j][k]

                else:
                    dfep['Ponto ' + str(k)] = list_valores_ep
            df_ep_f = expander.data_editor(dfep, disabled=[str(j) + '. Variável'])
            for n in range(n_pontos_ep):
                ep.append(list(df_ep_f['Ponto ' + str(n)]))


        expander.divider()
        contr_difusa = expander.checkbox(str(j) + '. Possui algum ponto de **contribuição difusa**.',
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
                            'Comprimento final (m)',
                            'Vazão TOTAL (m³/s)']
            list_valores_ed = [None, None, None, None, None, None, None]
            list_name_f = list_name
            del(list_name_f[0])
            list_name_ed.extend(list_name_f)
            list_valores_ed.extend(list_valores)
            dfed = pd.DataFrame({str(j) + '. Variável': list_name_ed})
            for k in range(n_pontos_ed):
                if data != False:
                    dfed['Ponto ' + str(k)] = data['Contr e Retir'][2][j][k]

                else:
                    dfed['Ponto ' + str(k)] = list_valores_ed
            df_ed_f = expander.data_editor(dfed, disabled=[str(j) + '. Variável'])
            for n in range(n_pontos_ed):
                ed.append(list(df_ed_f['Ponto ' + str(n)]))
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
                  list_name, list_valores):
    col_1, col_2 = st.columns(2)
    salvar = col_2.toggle('Salvar dados preenchidos.')
    if salvar:
        data = {'dados': [{'Paramêtros': lista_modelagem, 'Dados gerais': lista_parametros,
                'Coeficientes': lista_coeficiente, 'Contr e Retir': lista_contr_retir,
                'Nomes': list_name, 'Valores': list_valores}]}
        from json import dumps
        json_string = dumps(data)

        col_1.download_button(
            label="Clique para fazer o Download",
            file_name="DadosEntrada.json",
            mime="application/json",
            data=json_string,
        )
    return

