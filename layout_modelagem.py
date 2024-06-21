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

    with col_1:
        st.markdown('Qual(s) parâmetro(s) modelar?')
        col_1_1, col_1_2 = st.columns(2)
        modelar_od = col_1_1.checkbox('OD', value=paramentro[0])
        if modelar_od:
                modelar_k_2 = col_1_1.checkbox('k2 tabelado', value=paramentro[1])
        else:
            modelar_k_2 = False
        modelar_dbo = col_1_1.checkbox('DBO', value=paramentro[2])
        modelar_n = col_1_2.checkbox('Nitrogênio', value=paramentro[3])
        modelar_p = col_1_2.checkbox('Fósforo', value=paramentro[4])
        modelar_colif = col_1_2.checkbox('Coliformes', value=paramentro[5])
    n_tributarios = col_2.number_input(
        'Quantidade de tributários modeláveis:',
        min_value=0, value=paramentro[6])
    lista_modelagem = [modelar_od, modelar_k_2, modelar_dbo, modelar_n,
                       modelar_p, modelar_colif, n_tributarios]

    lista_tabs = ["tab0"]
    labels = ["Rio principal"]
    for n_trib in range(n_tributarios):
        lista_tabs.append("tab" + str(n_trib))
        labels.append("Tributário " + str(n_trib + 1))
    lista_tabs = st.tabs(labels)

    return (lista_modelagem, data, labels, lista_tabs)

##################################################################
######################### DADOS INICIAIS ##########################
def dados_iniciais(data, lista_modelagem, n_tributarios, labels, lista_tabs):
    # DADOS DE ENTRADA INICIAIS
    list_valor_i = []
    list_discretizacao = []
    list_comprimento = []
    list_longitude = []
    list_latitude = []
    list_altitude = []
    list_secaotrav = []

    
    list_name_hid = ['Latitude (UTM)',
                    'Longitude (UTM)',
                    'Comprimento (m)',
                    'Rugosidade (manning)',
                    'Largura (m)',
                    'Ângulo esquerdo (°)',
                    'Ângulo direito (°)']
    list_valores_hid = [None, None, None, 0.0, 0.0, 0.0, 0.0]

    for i in range(n_tributarios + 1):
        comprimento = []
        longitude = []
        latitude = []
        altitude = []
        preecheu = False
        expander = lista_tabs[i].expander(
            "**:orange[DADOS DE ENTRADA INICIAIS]**")
        col_11, col_12 = expander.columns(2)
        col_121, col_122 = col_12.columns(2)
        alter_espacial = True
        if data != False:
            alter_espacial = col_11.toggle('Alterar variáveis espaciais.')
        if alter_espacial:
            
            discret = col_122.number_input(
                str(i) + '. Discretização (m)', value=50.0,
                min_value=0.1, step=1e-2, format="%.2f")
            
            tipo_entrada = col_11.radio(str(i) + ". Tipo de entrada dos dados espaciais:",
                                        ["Intervalo", "Manual","GeoJSON"],
                                        horizontal=True)
            col_111, col_112 = col_11.columns(2)
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

                expander.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                        icon="❕")
                df_espacial = expander.data_editor(df_esp, num_rows="dynamic")
                if len(df_espacial[str(i) + '. Latitude (UTM)']) > 0:
                    if df_espacial[str(i) + '. Latitude (UTM)'][0] == None:
                        comprimento = list(df_espacial.iloc[:,3])
                    else:
                        latitude = list(df_espacial.iloc[:,0])
                        longitude = list(df_espacial.iloc[:,1])
                        preecheu = True
                    altitude = list(df_espacial.iloc[:,2])


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

            expander.divider()
        col1, col2 = expander.columns(2)
        alter_var_i = True
        if data != False:
            alter_var_i = col1.toggle('Alterar variáveis iniciais de vazão e concentrações.')
        if alter_var_i:
            
            col1.markdown(":orange[Variáveis iniciais do " + str(labels[i]) + ":]")
            
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
                list_name.append('E-coli (mg/L)')
                list_valores.append(0.0)
                
            df_conc = pd.DataFrame({str(i) + '. Descrição': list_name, 'Valores': list_valores})
            df_espacial = col1.data_editor(df_conc, disabled=[str(i) + '. Descrição'])

        if alter_espacial:
            if preecheu:
                on = col2.toggle("Visualizar dados espaciais")
                zona = col_111.number_input(
                    str(i) + '. WGS 84 - UTM - Zona:', min_value=0, value=22)
                hemisferio = col_112.radio(str(i) + '. Hemisfério:', ['Sul', 'Norte'],
                                        horizontal=True)
            
                if on:
                    if hemisferio == 'Sul':
                        hemisferio = 'south'
                    else:
                        hemisferio = 'north'

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
                        altitude.append((k * incl) + altit) 
        
        alter_sectr = True
        if data != False:
            alter_sectr = expander.toggle('Alterar valores das secções transversais.')
        if alter_sectr:
            expander.divider()
            expander.markdown(":orange[Secções transversais do " + str(labels[i]) + ":]")
            col_3_1, col_3_2 = expander.columns(2)
            n_pontos = col_3_1.number_input(
                str(i) + '. Quantidade de pontos que alteram os valores'
                + ' de uma ou mais variáveis hidráulicas:',
                min_value=0)
            df_hid = pd.DataFrame({str(i) + '. Descrição': list_name_hid})
            for k in range(n_pontos + 1):
                df_hid['Ponto ' + str(k)] = list_valores_hid
            df_hid_f = expander.data_editor(df_hid, disabled=[str(i) + '. Descrição'])
            hidr = []
            for k in range(n_pontos + 1):
                hidr.append(list(df_hid_f['Ponto ' + str(k)]))

        if alter_espacial:
            list_comprimento.append(comprimento)
            list_longitude.append(longitude)
            list_latitude.append(latitude)
            list_altitude.append(altitude)
            list_discretizacao.append(discret)
        else:
            list_comprimento = data['Dados gerais'][1]
            list_longitude = data['Dados gerais'][2]
            list_latitude = data['Dados gerais'][3]
            list_altitude = data['Dados gerais'][4]
            list_discretizacao = data['Dados gerais'][6]
        
        if alter_var_i:
            list_valor_i.append(list(df_espacial['Valores']))
        else:
            list_valor_i = data['Dados gerais'][0]
            list_name = data['Nomes']
            list_valores = data['Valores']
        
        if alter_sectr:
            list_secaotrav.append(hidr)
        else:
            list_secaotrav = data['Dados gerais'][5]


    lista_parametros = [list_valor_i, list_comprimento, list_longitude,
                        list_latitude, list_altitude, list_secaotrav, list_discretizacao]
    return lista_parametros, list_name, list_valores


########################## COEFICIENTES ###########################
def coeficientes(data, lista_modelagem, n_tributarios, labels, lista_tabs):
    # COEFICIENTES DDO MODEDELO

    list_name = ['Latitude (UTM)',
                 'Longitude (UTM)',
                 'Comprimento (m)',
                 'Temperatura (°C)']
    list_valores = [None, None, None, 22.0]
    if lista_modelagem[1]:
        list_name.append('k2 (1/d)')
        list_valores.append(0.0)
    if lista_modelagem[0]:
        list_name.extend(['k2 máximo (1/d)',
                          'k1 (1/d)',
                          'kd (1/d)',
                          'ks (1/d)',
                          'lrd (gDBO5/m.d)',
                          'sd (1/d)'])
        list_valores.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
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
            min_value=0)
        df_coef = pd.DataFrame({str(i) + '. Descrição': list_name})        
        for k in range(n_pontos + 1):
            df_coef['Ponto ' + str(k)] = list_valores
        df_coef_f = expander.data_editor(df_coef, disabled=[str(i) + '. Descrição'])
        coef = []
        for k in range(n_pontos + 1):
            coef.append(list(df_coef_f['Ponto ' + str(k)]))

        lista_coeficiente.append(coef)
    return lista_coeficiente


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

    for j in range(n_tributarios + 1):
        
        expander = lista_tabs[j].expander("**:blue[CONTRIBUIÇÕES E RETIRADAS]**")

        retiradas = expander.checkbox(str(j) + '. Possui algum ponto de **captação de água**.')
        ret = []
        if retiradas:
            col4_1, col4_2 = expander.columns(2)
            col4_1.markdown(":blue[Retiradas do " + str(labels[j]) + ":]")
            col4_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                           icon="❕")
            n_pontos_r = col4_1.number_input(
                str(j) + '. Quantidade de ponto de captação:',
                min_value=0)
            list_name_ret = list_name_cr + ['Vazão (m³/s)']
            list_valores_ret = list_valores_cr  + [0.0]
            dfret = pd.DataFrame({str(j) + '. Variável': list_name_ret})
            for k in range(n_pontos_r + 1):
                dfret['Ponto ' + str(k)] = list_valores_ret
            df_ret_f = expander.data_editor(dfret, disabled=[str(j) + '. Variável'])
            for n in range(n_pontos_r + 1):
                ret.append(list(df_ret_f['Ponto ' + str(n)]))


        expander.divider()
        contr_pontual = expander.checkbox(str(j) + '. Possui algum ponto de **contribuição pontual**.')
        ep = []
        if contr_pontual:
            col4_1, col4_2 = expander.columns(2)
            col4_1.markdown(":blue[Contribuições pontuais do " + str(labels[j]) + ":]")
            col4_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                           icon="❕")
            n_pontos_ep = col4_1.number_input(
                str(j) + '. Quantidade de pontos de entradas pontuais:',
                min_value=0)
            list_name_ep = list_name_cr + list_name
            list_valores_ep = list_valores_cr  + list_valores
            dfep = pd.DataFrame({str(j) + '. Variável': list_name_ep})
            for k in range(n_pontos_ep + 1):
                dfep['Ponto ' + str(k)] = list_valores_ep
            df_ep_f = expander.data_editor(dfep, disabled=[str(j) + '. Variável'])
            for n in range(n_pontos_ep + 1):
                ep.append(list(df_ep_f['Ponto ' + str(n)]))


        expander.divider()
        contr_difusa = expander.checkbox(str(j) + '. Possui algum ponto de **contribuição difusa**.')
        ed = []
        if contr_difusa:
            col4_1, col4_2 = expander.columns(2)
            col4_1.markdown(":blue[Contribuições difusa do " + str(labels[j]) + ":]")
            col4_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                           icon="❕")
            n_pontos_ed = col4_1.number_input(
                str(j) + '. Quantidade de pontos de entradas difusas:',
                min_value=0)
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
            for k in range(n_pontos_ed + 1):
                dfed['Ponto ' + str(k)] = list_valores_ed
            df_ed_f = expander.data_editor(dfed, disabled=[str(j) + '. Variável'])
            for n in range(n_pontos_ed + 1):
                ed.append(list(df_ed_f['Ponto ' + str(n)]))
        expander.divider()
        list_retiradas.append(ret)
        list_ep.append(ep)
        list_ed.append(ed)
    
    lista_contr_retir = [ret, ep, ed]

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