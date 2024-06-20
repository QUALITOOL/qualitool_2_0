import streamlit as st
import pandas as pd
import numpy as np



def inicio():

    st.divider()
    dados_anterior = st.checkbox("Preenchimento automático.")
    if dados_anterior:
        uploaded_file = st.file_uploader("Submeter o arquivo 'DadosEntrada.xlsx'"
                                         + " construído anteriormente:",
                                         type=["xlsx"])
        if uploaded_file is not None:
            dataframe = pd.read_excel(uploaded_file)
            st.write(dataframe)
        else:
            st.markdown("""❗ Obs.: Evite alterar o arquivo 'DadosEntrada.xlsx'
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
        modelar_od = col_1_1.checkbox('OD', value=True)
        if modelar_od:
                modelar_k_2 = col_1_1.checkbox('k2 tabelado')
        else:
            modelar_k_2 = False
        modelar_dbo = col_1_1.checkbox('DBO', value=True)
        modelar_n = col_1_2.checkbox('Nitrogênio', value=True)
        modelar_p = col_1_2.checkbox('Fósforo', value=True)
        modelar_colif = col_1_2.checkbox('Coliformes', value=True)
    n_tributarios = col_2.number_input(
        'Quantidade de tributários modeláveis:',
        min_value=0)
    lista_modelagem = [modelar_od, modelar_k_2, modelar_dbo, modelar_n,
                       modelar_p, modelar_colif]

    lista_tabs = ["tab0"]
    labels = ["Rio principal"]
    for n_trib in range(n_tributarios):
        lista_tabs.append("tab" + str(n_trib))
        labels.append("Tributário " + str(n_trib + 1))
    lista_tabs = st.tabs(labels)

    return (lista_modelagem, n_tributarios, labels, lista_tabs)



############################ DADOS INICIAIS #############################
def dados_iniciais(lista_modelagem, n_tributarios, labels, lista_tabs):
    # DADOS DE ENTRADA INICIAIS
    list_valor_i = []
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
        with col_11:
            tipo_entrada = st.radio(str(i) + ". Tipo de entrada dos dados espaciais:",
                                        ["Intervalo", "Manual","GeoJSON"],
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
                import geopandas as gpd
                gdf = gpd.read_file(df_espacial)
                preecheu = True
                for x in range(len(gdf)):
                    longitude.append(gdf["geometry"][x].x)
                    latitude.append(gdf["geometry"][x].y)

                altitude = list(gdf.iloc[:,1])

        expander.divider()
        col1, col2 = expander.columns(2)

        with col1:
            st.markdown(":orange[Variáveis iniciais do " + str(labels[i]) + ":]")
            
            discret = col1.number_input(
                str(i) + '. Discretização (m)', value=50.0,
                min_value=0.1, step=1e-2, format="%.2f")
            
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
            df_espacial = st.data_editor(df_conc, disabled=[str(i) + '. Descrição'])


        with col2:
            if preecheu:
                on = st.toggle("Visualizar dados espaciais")
                zona = col_121.number_input(
                    str(i) + '. WGS 84 - UTM - Zona:', min_value=0, value=22)
                hemisferio = col_122.radio(str(i) + '. Hemisfério:', ['Sul', 'Norte'],
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
                    st.map(df_plot, size = 1, color='#007FFF')
            else:       
                if tipo_entrada == "Intervalo":
                    comprimento = list(np.arange(0.0, comp + discret, discret))
                    for k in range(len(comprimento)):
                        altitude.append((k * incl) + altit) 
        
        expander.divider()
        expander.markdown(":orange[Secções transversais do " + str(labels[i]) + ":]")
        col_3_1, col_3_2 = expander.columns(2)
        n_pontos = col_3_1.number_input(
            str(i) + '. Quantidade de ponto que alteram os valores'
            + ' de uma ou mais variáveis hidráulicas:',
            min_value=0)
        df_hid = pd.DataFrame({str(i) + '. Descrição': list_name_hid})        
        for k in range(n_pontos + 1):
            df_hid['Ponto ' + str(k)] = list_valores_hid
        df_hid_f = expander.data_editor(df_hid, disabled=[str(i) + '. Descrição'])
        hidr = []
        for k in range(n_pontos + 1):
            hidr.append(list(df_hid_f['Ponto ' + str(k)]))


        list_comprimento.append(comprimento)
        list_longitude.append(longitude)
        list_latitude.append(latitude)
        list_altitude.append(altitude)
        list_valor_i.append(list(df_espacial['Valores']))
        list_secaotrav.append(hidr)

    lista_parametros = [list_valor_i, list_comprimento, list_longitude,
                        list_latitude, list_altitude, list_secaotrav]
    return lista_parametros


############################ COEFICIENTES #############################
def coeficientes(lista_modelagem, n_tributarios, labels, lista_tabs):
    # COEFICIENTES DDO MODEDELO

    list_name = ['Latitude (UTM)',
                 'Longitude (UTM)',
                 'Comprimento (m)',
                 'Temperatura (°C)']
    list_valores = [None, None, None, 22.0]
    if lista_modelagem[1]:
        list_name.extend(['k2 (1/d)',
                            'k2 máximo (1/d)'])
        list_valores.extend([0.0, 0.0])
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


############################ RETIRADAS #############################
def fun_retiradas(lista_modelagem, n_tributarios, labels, lista_tabs):
    # RETIRADAS
    retirada = []
    lista_n_retiradas = []
    lista_dist_retiradas = []
    lista_q_retiradas = []
    for j in range(n_tributarios + 1):
        expander_0 = lista_tabs[j].expander("**:blue[RETIRADAS]**")
        mensagem = (
            'Possui algum ponto de captação de água no '
            + str(labels[j]))
        retiradas = expander_0.checkbox(mensagem)

        retirada.append(retiradas)
        if retirada[j]:
            n_retiradas = expander_0.number_input(
                'Número de retiradas do '
                + str(labels[j]),
                min_value=1)
            lista_n_retiradas.append(n_retiradas)
            lista_tabs_ret = []
            labels_ret = []
            for n_ret in range(lista_n_retiradas[j]):
                lista_tabs_ret.append("tab" + str(n_ret))
                labels_ret.append("Retirada " + str(n_ret + 1))
            lista_tabs_ret = expander_0.tabs(labels_ret)

            dist_retiradas = []
            q_retiradas = []
            for n_ret in range(lista_n_retiradas[j]):
                dist_retirada = lista_tabs_ret[n_ret].number_input(
                    'Distância da ' + str(labels_ret[n_ret]) + ' com o '
                    + str(labels[j]) + ' (km)',
                    min_value=0.0, step=1e-3, format="%.3f")
                dist_retiradas.append(dist_retirada)
                q_retirada = lista_tabs_ret[n_ret].number_input(
                    'Vazão da ' + str(labels_ret[n_ret]) + ' do '
                    + str(labels[j]),
                    min_value=0.0, step=1e-3, format="%.3f")
                q_retiradas.append(q_retirada)
            lista_dist_retiradas.append(dist_retiradas)
            lista_q_retiradas.append(q_retiradas)
    lista_retirada = [lista_dist_retiradas, lista_q_retiradas, retirada]
    return lista_retirada


def fun_despejos(lista_modelagem, n_tributarios, labels, lista_tabs):
    # DESPEJOS
    despejo = []
    lista_n_despejos = []
    lista_dist_despejos = []
    lista_q_despejos = []
    lista_od_despejos = []
    list_dbo5_desp = []
    list_norgr_desp = []
    list_namonr_desp = []
    list_enitritor_desp = []
    list_nnitrator_desp = []
    list_porgr_desp = []
    list_pinorgr_desp = []
    list_colif_desp = []
    for i in range(n_tributarios + 1):
        expander_1 = lista_tabs[i].expander("**:blue[DESPEJOS]**")
        mensagem = (
            'Possui algum ponto de despejo de despejo no '
            + str(labels[i]))
        despejos = expander_1.checkbox(mensagem)
        despejo.append(despejos)

        if despejo[i]:
            n_despejos = expander_1.number_input(
                'Número de despejos do '
                + str(labels[i]), min_value=1)
            lista_n_despejos.append(n_despejos)

            lista_tabs_desp = []
            labels_desp = []

            for n_desp in range(lista_n_despejos[i]):
                lista_tabs_desp.append("tab_desp" + str(n_desp))
                labels_desp.append("Despejo " + str(n_desp + 1))
            lista_tabs_desp = expander_1.tabs(labels_desp)

            dist_despejos = []
            q_despejos = []
            od_despejos = []
            dbo5_desp = []
            norgr_desp = []
            namonr_desp = []
            enitritor_desp = []
            nnitrator_desp = []
            porgr_desp = []
            pinorgr_desp = []
            colif_desp = []
            for n_desp in range(lista_n_despejos[i]):
                col_d1, col_d2 = lista_tabs_desp[n_desp].columns(2)
                with col_d1:
                    st.markdown("##### :orange[Dados gerais:]")
                    dist_despejo = st.number_input(
                        'Distância da ' + str(labels_desp[n_desp])
                        + ' com o ' + str(labels[i]) + ' (km)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    dist_despejos.append(dist_despejo)
                    q_despejo = st.number_input(
                        'Vazão da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i]),
                        min_value=0.0, step=1e-3, format="%.3f")
                    q_despejos.append(q_despejo)
                    od_despejo = st.number_input(
                        'OD da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i]) + ' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    od_despejos.append(od_despejo)
                    dbo5_despejo = st.number_input(
                        'DBO5 da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i]) + ' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    dbo5_desp.append(dbo5_despejo)
                    st.markdown("##### :orange[Fósforo:]")
                    porgr_despejo = st.number_input(
                        'P orgânico da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i])
                        + ' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    porgr_desp.append(porgr_despejo)
                    pinorgr_despejo = st.number_input(
                        'P inorgânico da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i])
                        + ' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    pinorgr_desp.append(pinorgr_despejo)
                with col_d2:
                    st.markdown("##### :orange[Nitrogênio:]")
                    norgr_despejo = st.number_input(
                        'Nitrogênio orgânico da ' + str(labels_desp[n_desp])
                        + ' do '
                        + str(labels[i])+' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    norgr_desp.append(norgr_despejo)
                    namonr_despejo = st.number_input(
                        'Amônia-N da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i])
                        + ' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    namonr_desp.append(namonr_despejo)
                    enitritor__despejo = st.number_input(
                        'Nitrito-N da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i])
                        + ' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    enitritor_desp.append(enitritor__despejo)
                    nnitrator_despejo = st.number_input(
                        'Nitrato-N da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i])
                        + ' (mg/L)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    nnitrator_desp.append(nnitrator_despejo)
                    st.markdown("##### :orange[Coliformes:]")
                    colif_despejo = st.number_input(
                        'Coliformes da ' + str(labels_desp[n_desp])
                        + ' do ' + str(labels[i])
                        + ' (NMP/100ml)',
                        min_value=0.0, step=1e-3, format="%.3f")
                    colif_desp.append(colif_despejo)
            lista_dist_despejos.append(dist_despejos)
            lista_q_despejos.append(q_despejos)
            lista_od_despejos.append(od_despejos)
            list_dbo5_desp.append(dbo5_desp)
            list_norgr_desp.append(norgr_desp)
            list_namonr_desp.append(namonr_desp)
            list_enitritor_desp.append(enitritor_desp)
            list_nnitrator_desp.append(nnitrator_desp)
            list_porgr_desp.append(porgr_desp)
            list_pinorgr_desp.append(pinorgr_desp)
            list_colif_desp.append(colif_desp)
    lista_despejo = [lista_dist_despejos, lista_q_despejos,
                     lista_od_despejos, list_dbo5_desp, list_norgr_desp,
                     list_namonr_desp, list_enitritor_desp,
                     list_nnitrator_desp, list_porgr_desp, list_pinorgr_desp,
                     list_colif_desp, despejo]

    return lista_despejo
