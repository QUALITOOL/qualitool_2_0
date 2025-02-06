import streamlit as st
import pandas as pd


def inicio_calib(paramentro):
    
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
    modelar_od = col_1_1.checkbox('OD e DBO', value=paramentro['m_od'], disabled=disab)
    modelar_dbo = modelar_od
    modelar_n = col_1_1.checkbox('Nitrogênio', value=paramentro['m_n'], disabled=disab)
    modelar_p = col_1_2.checkbox('Fósforo', value=paramentro['m_p'], disabled=disab)
    modelar_colif = col_1_2.checkbox('Coliformes', value=paramentro['m_c'], disabled=disab)

    col_2.markdown('Configurações gerais:')
    serie_tempo = col_2.toggle('Ativar avaliação temporal.', value=paramentro['s_t'], disabled=disab)

    n_tributarios = col_2.number_input(
        'Quantidade de tributários modeláveis:', min_value=0,
        value=paramentro['n_tb'], disabled=disab)
    
    
    lista_modelagem = {'m_od': modelar_od, 'm_dbo': modelar_dbo, 'm_n': modelar_n,
                       'm_p': modelar_p, 'm_c': modelar_colif, 'n_tb': n_tributarios,
                       's_t': serie_tempo}

    alterar_par_pso = st.checkbox(":grey[Configurações avançadas.]")

    if alterar_par_pso:
        st.markdown('Parâmetros do PSO:')
        col1, col2 = st.columns(2)
        col2_1, col2_2 = col2.columns(2)
        tam_enxame = col2_1.number_input("❗ Tamanho do enxame:", value=15, min_value=1)
        n_ger = col2_2.number_input("❗ Número de interações", value=30, min_value=1)
        col2.warning('''Cuidado: Quanto maior for o tamanho do enxame ou o número de interações, 
                        maior será o tempo necessário para gerar os resultados.''',
                    icon="❗")
        w = col1.slider("Inércia:", 0.0, 2.0, 0.9)
        col1_1, col1_2 = col1.columns(2)
        c1 = col1_1.slider("Componente cognitiva (pessoal):", 0.0, 2.0, 1.8)
        c2 = col1_2.slider("Componente social (global):", 0.0, 2.0, 2.0)
    
    else:
        tam_enxame = 15
        n_ger = 15
        w = 0.9
        c1 = 1.8
        c2 = 2.0

    lista_par_pos = [tam_enxame, n_ger, w, c1, c2]

    lista_tabs = ["tab0"]
    labels = ["Rio principal"]
    for n_trib in range(n_tributarios):
        lista_tabs.append("tab" + str(n_trib))
        labels.append("Tributário " + str(n_trib + 1))
    lista_tabs = st.tabs(labels)


    return lista_modelagem, data, labels, lista_tabs, lista_par_pos


def coef_intervalo(lista_modelagem, n_tributarios, labels, lista_tabs):
    # COEFICIENTES DDO MODEDELO

    lista_n_pontos = []
    list_name_c2 = ['Temperatura (°C)']
    list_valores_c2_mx = [24.0]
    list_valores_c2_mn = [19.0]
    if lista_modelagem['m_od']:
        list_name_c2.extend(['k1 (1/d)', 'k2 (1/d)', 'kd (1/d)',
                                'ks (1/d)', 'lrd (gDBO5/m.d)',
                                'sd (1/d)'])
        
        list_valores_c2_mx.extend([0.45, 100.0, 1.0, 0.35, 1.0, 10.0])
        list_valores_c2_mn.extend([0.08, 0.05, 0.08, 0.05, 0.05, 0.05])
                        
    if lista_modelagem['m_od'] == True and lista_modelagem['m_n'] == True:
        list_name_c2.append('O2namon (mgO2/mgNamon oxid)')
        list_valores_c2_mx.append(4.0)
        list_valores_c2_mn.append(3.0)
    if lista_modelagem['m_n']:
        list_name_c2.extend(['koa (1/d)',
                        'kso (1/d)',
                        'kan (1/d)',
                        'Snamon (g/m2.d)',
                        'knn (1/d)',
                        'knitr (1/d)'])
        list_valores_c2_mx.extend([0.25, 0.10, 0.25, 0.5, 1.0, 1.0])
        list_valores_c2_mn.extend([0.15, 0.001, 0.15, 0.001, 0.1, 0.1])
    if lista_modelagem['m_p']:
        list_name_c2.extend(['koi (1/d)',
                            'kspo (1/d)',
                            'spinorg (1/d)'])
        list_valores_c2_mx.extend([0.3, 0.5, 0.2])
        list_valores_c2_mn.extend([0.2, 0.02, 0.001])
    if lista_modelagem['m_c']:
        list_name_c2.append('kb (1/d)')
        list_valores_c2_mx.append(1.5)
        list_valores_c2_mn.append(0.05)

    lista_coeficiente = [list_name_c2]

    list_name_c = ['Latitude (UTM)', 'Longitude (UTM)', 'Comprimento (m)']
    list_valores_c = [None, None, 0.0]
    list_calb_trib = []

    for i in range(n_tributarios + 1):

        expander = lista_tabs[i].expander(
            "**:green[INTERVALOS DE BUSCA DOS COEFICIENTES]**")

        calb_trib = False

        if i != 0:
            calb_trib = expander.checkbox('Calibrar ' + str(labels[i]) + '.')
        else:
            calb_trib = True
            
        list_calb_trib.append(calb_trib)

        if calb_trib == True or i == 0:

            col_11, col_21 = expander.columns(2)
            col_21.warning('''Adicionar ou a **Longitude e Latitude** ou o **Comprimento**.''',
                                icon="❕")

            expander.markdown(":green[Variáveis do " + str(labels[i]) +":]")
            
            n_pontos = col_11.number_input(
                str(i) + '. Quantidade de pontos que alteram os valores'
                + ' de um ou mais coeficientes:',
                min_value=0)
            lista_n_pontos.append(n_pontos)

            df_coef = pd.DataFrame({str(i) + '. Descrição': list_name_c})
            for k in range(n_pontos + 1):
                df_coef['Ponto ' + str(k)] = list_valores_c
            df_coef_f = expander.data_editor(df_coef, disabled=[str(i) + '. Descrição'])
            
            list_c1 = []
            for n_p in range(n_pontos + 1):
                list_c1.append(list(df_coef_f['Ponto ' + str(n_p)]))

            expander.markdown(":green[Intervalos de busca do " + str(labels[i]) +":]")

        else: 
            lista_n_pontos.append(n_pontos)
            list_c1 = list_valores_c


        coef_igual = True
        if calb_trib and i != 0:
            coef_igual = expander.checkbox('Intervalos do ' +
                                            str(labels[i])
                                            + ' serão iguais aos do Rio Principal.',
                                            value=True)

        if coef_igual == False or i == 0:
            df_coef2 = pd.DataFrame(columns=[str(i) + '. Nome', 'Mínimo', 'Máximo'])

            df_coef2[str(i) + '. Nome'] = list_name_c2
            df_coef2['Mínimo'] = list_valores_c2_mn
            df_coef2['Máximo'] = list_valores_c2_mx


            df_coef2_f = expander.data_editor(df_coef2,
                                            disabled=[str(i) + '. Nome'])
            
            if i == 0:
                coef_min_0 = df_coef2_f['Mínimo']
                coef_max_0 = df_coef2_f['Máximo']
                
            coef_min = df_coef2_f['Mínimo']
            coef_max = df_coef2_f['Máximo']

        else:
            coef_min = coef_min_0
            coef_max = coef_max_0

        lista_coeficiente.append([list_c1, [coef_min, coef_max]])
                
           
        

    list_coef_f = {'l_coe': lista_coeficiente, 'l_n_p': lista_n_pontos, 'calb_trib': list_calb_trib}
    return list_coef_f


def dados_reais(n_tributarios, labels, lista_tabs, list_name, list_valores,
                lista_modelagem, dados_calib):

   
    lista_n_pontos = []

    list_name_dr_1 = ['ID (opcional)', 'Latitude (UTM)', 'Longitude (UTM)', 'Comprimento (m)']
    list_valores_c = [0, None, None, 0.0]
    list_dr = []
    
    for i in range(n_tributarios + 1):
        dr = []
        if i == 0 or dados_calib['calb_trib'][i - 0] == True:

            expander = lista_tabs[i].expander("**:red[DADOS OBSERVADOS]**")

            col_11, col_21 = expander.columns(2)
            col_21.warning('''Adicionar ou a **Longitude e Latitude** ou o **Comprimento**.''',
                                icon="❕")

            expander.markdown(":green[Variáveis do " + labels[i] +":]")

            n_pontos = col_11.number_input(
                str(i) + '. Quantidade de pontos observados no ' + labels[i] + ':',
                min_value=dados_calib['l_n_p'][i] + 1)
            
            lista_n_pontos.append(n_pontos)

            df_coef_dr = pd.DataFrame({str(i) + '. Descrição': list_name_dr_1})
            labels_dr = []
            for k in range(n_pontos):
                df_coef_dr['Ponto ' + str(k + 1)] = list_valores_c
                labels_dr.append(str(i) + '. Ponto ' + str(k + 1))
            df_coef_f = expander.data_editor(df_coef_dr, disabled=[str(i) + '. Descrição'])
            

            tabs_dr = expander.tabs(labels_dr)

            for tdr in range(len(labels_dr)):

                if lista_modelagem['s_t']:
                    list_name_dr = ['Data', str(i) + '.' + str(tdr) +'. Q (m³/s)'] + list_name
                else:
                    list_name_dr = [str(i) + '.' + str(tdr) +'. Q (m³/s)'] + list_name
                
                list_valores_dr = [[0.0]] + list_valores
                df_dr2 = pd.DataFrame(columns=list_name_dr)
              
                
                for yc in range(len(list_name_dr)):
                    if lista_modelagem['s_t'] == True:
                        if yc == 0:
                            df_dr2[list_name_dr[yc]] = [None]
                        else:
                            df_dr2[list_name_dr[yc]] = list_valores_dr[yc - 1]
                    else:
                        df_dr2[list_name_dr[yc]] = list_valores_dr[yc]


                df_dr2_f = tabs_dr[tdr].data_editor(df_dr2, num_rows="dynamic",
                                                   column_config={
                                                       'Data':st.column_config.DateColumn(
                                                           format="MM.DD.YYYY", step=1),
                                                        str(i) + '.' + str(tdr) +'. Q (m³/s)':st.column_config.NumberColumn(min_value=0),
                                                        'OD (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'DBO (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'N-org (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'N-amon (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'N-nitri (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'N-nitra (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'P-org (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'P-inorg (mg/L)':st.column_config.NumberColumn(min_value=0),
                                                        'E-coli (NMP/100ml)':st.column_config.NumberColumn(min_value=0),
                                                        })
                list_valores_dr = []
                list_datas_dr = []
                for drf in range(len(list_name_dr)):
                    if drf == 0 and lista_modelagem['s_t'] == True:
                        list_datas_dr.append(pd.to_datetime(df_dr2_f[list_name_dr[drf]]))
                    else:
                        list_valores_dr.append(list(df_dr2_f[list_name_dr[drf]]))
                  
                dr.append([list(df_coef_f['Ponto ' + str(tdr + 1)]), list_valores_dr, list_datas_dr])
            
            list_dr.append(dr)
        

    lista_dados_reais = {'l_dr': list_dr, 'n_pontos': lista_n_pontos}

    return lista_dados_reais
