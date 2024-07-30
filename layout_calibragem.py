import streamlit as st
import pandas as pd


def inicio():
    col_1, col_2 = st.columns(2)

    classe_rio = col_2.slider(
        'Qual a classe do rio, segundo CONAMA n° 357/05?',
        1, 4, 2)

    col_1.warning('''Atenção! Caso a tela atualize os dados já preenchidos
                  serão pertidos e devão ser preenchidos novamente.''',
                  icon="⚠️")

    with col_1:
        st.markdown('Qual(s) parâmetro(s) modelar?')
        col_1_1, col_1_2 = st.columns(2)
        modelar_od = col_1_1.checkbox('OD')
        modelar_dbo = col_1_1.checkbox('DBO')
        modelar_n = col_1_1.checkbox('Nitrogênio')
        modelar_p = col_1_2.checkbox('Fósforo')
        modelar_colif = col_1_2.checkbox('Coliformes')
    n_tributarios = col_2.number_input(
        'Quantidade de tributários modeláveis:',
        min_value=0)
    lista_modelagem = [modelar_od, modelar_dbo, modelar_n,
                       modelar_p, modelar_colif]

    delta = col_2.number_input(
        'Delta de distância para integração '
        + ' de cada segmento (km):',
        min_value=0.100, step=1e-3, format="%.3f")


    uploaded_file = st.file_uploader("TESTE")
    if uploaded_file is not None:
        dataframe = pd.read_excel(uploaded_file)
        st.write(dataframe)

    lista_tabs = ["tab0"]
    labels = ["Rio principal"]
    for n_trib in range(n_tributarios):
        lista_tabs.append("tab" + str(n_trib))
        labels.append("Tributário " + str(n_trib + 1))
    lista_tabs = st.tabs(labels)


    return (lista_modelagem, n_tributarios,
            delta, labels, lista_tabs, classe_rio)




def dados_iniciais(lista_modelagem, n_tributarios, labels, lista_tabs):
    # DADOS DE ENTRADA INICIAIS
    list_qr = []
    list_od = []
    list_dbo5 = []
    list_temperatura = []
    list_altitude = []
    list_colif = []
    list_norgr = []
    list_namonr = []
    list_enitritor = []
    list_nnitrator = []
    list_porgr = []
    list_pinorgr = []
    list_dist_trib = []
    list_comp_trib = []

    for i in range(n_tributarios + 1):
        expander = lista_tabs[i].expander(
            "**:orange[DADOS DE ENTRADA INICIAIS]**")
        col1, col2 = expander.columns(2)

        with col1:
            st.markdown("##### :orange[Geral:]")
            if i > 0:
                dist_tributario = st.number_input(
                    'Ponto do ' + str(labels[i]) + ' em relação a montante' +
                    ' do Rio Principal (km)',
                    min_value=0.0, step=1e-3, format="%.3f")
                list_dist_trib.append(dist_tributario)
            comp_tributario = st.number_input(
                'Comprimento do ' + str(labels[i]) + ' (km)'
                + ' *a ser modelado*',
                min_value=150.0, step=1e-3, format="%.3f")
            list_comp_trib.append(comp_tributario)
            qr = st.number_input(
                'Vazão do ' + str(labels[i]) + ' (m³/s)',
                min_value=3.3, step=1e-3, format="%.3f")
            list_qr.append(qr)
            od = st.number_input(
                'OD do ' + str(labels[i]) + ' (mg/L)',
                min_value=15.540, step=1e-3, format="%.3f")
            list_od.append(od)
            dbo5 = st.number_input(
                'DBO5 do ' + str(labels[i]) + ' (mg/L)',
                min_value=8.0, step=1e-3, format="%.3f")
            list_dbo5.append(dbo5)
            temperatura = st.number_input(
                'Temperatura do ' + str(labels[i]) + ' (°C)',
                min_value=23.0, step=1e-3, format="%.3f")
            list_temperatura.append(temperatura)
            altitude = st.number_input(
                'Altitude acima do nível do mar do '
                + str(labels[i]) + ' (mg/L)',
                min_value=830.0, step=1e-3, format="%.3f")
            list_altitude.append(altitude)
        with col2:
            st.markdown("##### :orange[Nitrogênio:]")
            norgr = st.number_input(
                'Nitrogênio orgânico do '
                + str(labels[i])+' (mg/L)',
                min_value=0.2, step=1e-3, format="%.3f")
            list_norgr.append(norgr)
            namonr = st.number_input(
                'Amônia-N do ' + str(labels[i])
                + ' (mg/L)',
                min_value=0.5, step=1e-3, format="%.3f")
            list_namonr.append(namonr)
            enitritor = st.number_input(
                'Nitrito-N do ' + str(labels[i])
                + ' (mg/L)',
                min_value=0.1, step=1e-3, format="%.3f")
            list_enitritor.append(enitritor)
            nnitrator = st.number_input(
                'Nitrato-N do ' + str(labels[i])
                + ' (mg/L)',
                min_value=0.1, step=1e-3, format="%.3f")
            list_nnitrator.append(nnitrator)
            st.markdown("##### :orange[Fósforo:]")
            porgr = st.number_input(
                'P orgânico do ' + str(labels[i])
                + ' (mg/L)',
                min_value=0.01, step=1e-3, format="%.3f")
            list_porgr.append(porgr)
            pinorgr = st.number_input(
                'P inorgânico do ' + str(labels[i])
                + ' (mg/L)',
                min_value=0.02, step=1e-3, format="%.3f")
            list_pinorgr.append(pinorgr)
            st.markdown("##### :orange[Coliformes:]")
            colif = st.number_input(
                'Coliformes no ' + str(labels[i])
                + ' (NMP/100ml)',
                min_value=0.0, step=1e-3, format="%.3f")
            list_colif.append(colif)
    lista_parametros = [list_qr, list_od, list_dbo5, list_temperatura,
                        list_altitude, list_colif, list_norgr,
                        list_namonr, list_enitritor, list_nnitrator,
                        list_porgr, list_pinorgr,
                        list_dist_trib, list_comp_trib]
    return lista_parametros


def coeficientes(lista_modelagem, n_tributarios, labels, lista_tabs):
    # COEFICIENTES DDO MODEDELO
    list_kso = []
    list_koa = []
    list_kan = []
    list_knn = []
    list_o2namon = []
    list_o2nnitri = []
    list_knitr = []
    list_m = []
    list_n = []
    list_k2_max = []
    list_kspo = []
    list_koi = []
    list_kb = []
    list_snamon = []
    list_k1 = []
    list_kd = []
    list_ks = []
    list_spinorg = []
    list_fotossintese = []
    list_respiracao = []
    list_sedimento = []
    list_lrd = []
    for i in range(n_tributarios + 1):
        expander = lista_tabs[i].expander(
            "**:green[COEFICIENTES DO MODELO]**")
        col1, col2 = expander.columns(2)

        with col1:
            st.markdown("##### :green[Nitrogênio]")
            kso = st.number_input('kso: Coef. sedimentação Norg do '
                                  + str(labels[i]) + ' (1/d)',
                                  min_value=0.05, step=1e-3, format="%.3f")
            list_kso.append(kso)
            koa = st.number_input('koa: Coef. conversão Norg-Namon do '
                                  + str(labels[i]) + ' (1/d)',
                                  min_value=0.20, step=1e-3, format="%.3f")
            list_koa.append(koa)
            kan = st.number_input('kan: Coef. conversão Namon-Nnitrito do '
                                  + str(labels[i]) + ' (1/d)',
                                  min_value=0.150, step=1e-3, format="%.3f")
            list_kan.append(kan)
            knn = st.number_input('knn: Coef. conversão Nnitrito-Nnitrato do '
                                  + str(labels[i]) + ' (1/d)',
                                  min_value=0.80, step=1e-3, format="%.3f")
            list_knn.append(knn)
            snamon = st.number_input(
                'Snamon: Coef. liberação Namon pelo sedimento de fundo do '
                + str(labels[i]) + ' (g/m2.d)',
                min_value=0.40, step=1e-3, format="%.3f")
            list_snamon.append(snamon)
            o2namon = st.number_input(
                'O2namon: O2 equiv. conversão Namon-Nnitrito do '
                + str(labels[i])
                + ' (mgO2/mgNamon oxid)',
                min_value=3.2, step=1e-3, format="%.3f")
            list_o2namon.append(o2namon)
            o2nnitri = st.number_input(
                'O2nitri: O2 equiv. conversão Nnitrito-Nnitrato do '
                + str(labels[i]) + ' (mgO2/mgNnitrito oxid)',
                min_value=1.1, step=1e-3, format="%.3f")
            list_o2nnitri.append(o2nnitri)
            knitr = st.number_input(
                'knitr: Coef. inibição da nitrificação por baixo OD do '
                + str(labels[i]) + ' (1/d)',
                min_value=0.6, step=1e-3, format="%.3f")
            list_knitr.append(knitr)
            st.markdown("##### :green[Cargas difusas internas (sem vazão)]")
            fotossintese = st.number_input(
                "P': OD - Taxa produção de O2 por fotossíntese do "
                + str(labels[i]) + ' (g/m2.d)',
                min_value=0.0, step=1e-3,
                format="%.3f")
            list_fotossintese.append(fotossintese)
            respiracao = st.number_input(
                "R': OD - Taxa consumo de O2 por respiração do "
                + str(labels[i]) + ' (g/m2.d)',
                min_value=0.0, step=1e-3,
                format="%.3f")
            list_respiracao.append(respiracao)
            sedimento = st.number_input(
                "S': OD - Taxa consumo de O2 por demanda do sedimento do "
                + str(labels[i]) + ' (g/m2.d)',
                min_value=0.0, step=1e-3,
                format="%.3f")
            list_sedimento.append(sedimento)
            lrd = st.number_input(
                'lrd: DBO - Carga linear distribuída ao longo do '
                + str(labels[i]) + ' (gDBO5/m.d)',
                min_value=0.0, step=1e-3,
                format="%.3f")
            list_lrd.append(lrd)
        with col2:
            st.markdown("##### :green[Desoxigenação]")
            k1 = st.number_input(
                'k1: Coef. desoxigenação do ' + str(labels[i])
                + ' (1/d)', min_value=0.120, step=1e-3, format="%.3f")
            list_k1.append(k1)
            kd = st.number_input(
                'kd: Coef. sedimentação DBO do ' + str(labels[i])
                + ' (1/d)', min_value=0.120, step=1e-3, format="%.3f")
            list_kd.append(kd)
            ks = st.number_input(
                'ks: Coef. decomposição DBO do ' + str(labels[i])
                + ' (1/d)', min_value=0.0, step=1e-3, format="%.3f")
            list_ks.append(ks)
            st.markdown("##### :green[Reaeração - $$k2 = m * Q^{-n}$$]")
            m = st.number_input('m - Coef. reaeração do ' + str(labels[i]),
                                min_value=0.0, step=1e-3, format="%.3f")
            list_m.append(m)
            n = st.number_input('n - Coef. reaeração do ' + str(labels[i]),
                                min_value=0.0, step=1e-3, format="%.3f")
            list_n.append(n)
            k2_max = st.number_input('Valor máximo aceito para K2 do '
                                     + str(labels[i]),
                                     min_value=0.0, step=1e-3,
                                     format="%.3f")
            list_k2_max.append(k2_max)
            st.markdown("##### :green[Fósforo]")
            kspo = st.number_input('kspo: Coef. sedimentação Porg do '
                                   + str(labels[i]) + ' (1/d)',
                                   min_value=0.030, step=1e-3,
                                   format="%.3f")
            list_kspo.append(kspo)
            koi = st.number_input('koi: Coef. conversão Porg-Pinorg do '
                                  + str(labels[i]) + ' (1/d)',
                                  min_value=0.250, step=1e-3,
                                  format="%.3f")
            list_koi.append(koi)
            spinorg = st.number_input(
                'spiorg: Coef. liberação Pinorg pelo sedimento de fundo do '
                + str(labels[i]) + ' (g/m2.d)',
                min_value=0.10, step=1e-3, format="%.3f")
            list_spinorg.append(spinorg)
            st.markdown("##### :green[Coliformes]")
            kb = st.number_input('kb: Coef. decaimento de coliformes do '
                                 + str(labels[i]) + ' (1/d)',
                                 min_value=0.0, step=1e-3,
                                 format="%.3f")
            list_kb.append(kb)

        lista_coeficiente = [list_kso, list_koa, list_kan, list_knn,
                             list_o2namon, list_o2nnitri, list_knitr,
                             list_m, list_n, list_k2_max, list_kspo,
                             list_koi, list_kb, list_snamon, list_k1,
                             list_kd, list_ks, list_spinorg, list_fotossintese,
                             list_respiracao, list_sedimento, list_lrd]
    return lista_coeficiente


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
