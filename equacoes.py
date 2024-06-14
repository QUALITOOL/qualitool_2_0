import numpy as np


def velocidade_manning(vazao):
    sol = 0.897498340970115
    velocidade = 0.919221754892882

    return velocidade, sol


def velocidade(vazao):
    largura = 4
    inclinacao = 0.001
    manning = 0.025

    area = (largura * 0.897498340970115)
    velocidade = vazao / area
    return velocidade, 0.897498340970115


def mistura(concentracao1, vazao1, concentracao2, vazao2):
    mistura = ((concentracao1 * vazao1) + (concentracao2 * vazao2)) / (
        vazao1 + vazao2)
    return mistura


def k2_eq(list_m, list_n, list_k2_max, list_temperatura, index, vazao):
    k2_20 = list_m[index] * vazao ** (-list_n[index])
    if k2_20 > list_k2_max[index]:
        k2_20 = list_k2_max[index]
    k2 = k2_20 * 1.024 ** (list_temperatura[index] - 20)
    return k2


def equacoes(lista_parametros, lista_coeficientes, lista_despejos,
             lista_retirada, delta, index):

    list_qr = lista_parametros[0]
    list_od = lista_parametros[1]
    list_dbo5 = lista_parametros[2]
    list_temperatura = lista_parametros[3]
    list_altitude = lista_parametros[4]
    list_colif = lista_parametros[5]
    list_norgr = lista_parametros[6]
    list_namonr = lista_parametros[7]
    list_nnitritor = lista_parametros[8]
    list_nnitrator = lista_parametros[9]
    list_porgr = lista_parametros[10]
    list_pinorgr = lista_parametros[11]
    list_dist_trib = lista_parametros[12]
    list_comp = lista_parametros[13]

    list_kso = lista_coeficientes[0]
    kso = list_kso[index] * 1.024 ** (list_temperatura[index] - 20)
    list_koa = lista_coeficientes[1]
    koa = list_koa[index] * 1.047 ** (list_temperatura[index] - 20)
    list_kan = lista_coeficientes[2]
    kan = list_kan[index] * 1.080 ** (list_temperatura[index] - 20)
    list_knn = lista_coeficientes[3]
    knn = list_knn[index] * 1.047 ** (list_temperatura[index] - 20)
    list_o2namon = lista_coeficientes[4]
    list_o2nnitri = lista_coeficientes[5]
    list_knitr = lista_coeficientes[6]
    list_m = lista_coeficientes[7]
    list_n = lista_coeficientes[8]
    list_k2_max = lista_coeficientes[9]
    list_kspo = lista_coeficientes[10]
    kspo = list_kspo[index] * 1.024 ** (list_temperatura[index] - 20)
    list_koi = lista_coeficientes[11]
    koi = list_koi[index] * 1.047 ** (list_temperatura[index] - 20)
    list_kb = lista_coeficientes[12]
    kb = list_kb[index] * 1.07 ** (list_temperatura[index] - 20)
    list_snamon = lista_coeficientes[13]
    snamon = list_snamon[index] * 1.074 ** (list_temperatura[index] - 20)
    list_k1 = lista_coeficientes[14]
    k1 = list_k1[index] * 1.047 ** (list_temperatura[index] - 20)
    kt = 1 / (np.exp(-5 * k1))
    list_kd = lista_coeficientes[15]
    kd = list_kd[index] * 1.047 ** (list_temperatura[index] - 20)
    list_ks = lista_coeficientes[16]
    ks = list_ks[index] * 1.024 ** (list_temperatura[index] - 20)
    list_spinorg = lista_coeficientes[17]
    spinorg = list_spinorg[index] * 1.074 ** (list_temperatura[index] - 20)
    list_fotossintese = lista_coeficientes[18]
    taxa_fotossintese = list_fotossintese[index] * (
        1.047 ** (list_temperatura[index] - 20))
    list_respiracao = lista_coeficientes[19]
    taxa_respiracao = list_respiracao[index] * (
        1.047 ** (list_temperatura[index] - 20))
    list_sedimento = lista_coeficientes[20]
    taxa_sedimento = list_sedimento[index] * (
        1.06 ** (list_temperatura[index] - 20))
    list_lrd = lista_coeficientes[21]

    retirada = lista_retirada[2]
    despejo = lista_despejos[11]

    lista_delta = np.arange(0, list_comp[index], delta)
    vazao = list_qr[index]
    vaz_ant = vazao
    velocidade, profundidade = velocidade_manning(vazao)
    od = list_od[index]
    dbo5 = list_dbo5[index]
    od_saturacao = (1 - (list_altitude[index]/9450)) * (
        14.652 - (4.1022 * (10 ** -list_temperatura[index]))
        + (7.991 * 10 ** (-3) * (list_temperatura[index] ** 2))
        - (7.7774 * 10 ** (-5) * (list_temperatura[index] ** 3)))
    colif = list_colif[index]
    norgr = list_norgr[index]
    namonr = list_namonr[index]
    nnitritor = list_nnitritor[index]
    nnitrator = list_nnitrator[index]
    porgr = list_porgr[index]
    pinorgr = list_pinorgr[index]
    list_qr_final = []
    list_od_final = []
    list_dbo5_final = []
    list_colif_final = []
    list_norgr_final = []
    list_namonr_final = []
    list_nnitritor_final = []
    list_nnitrator_final = []
    list_porgr_final = []
    list_pinorgr_final = []
    list_n_total_final = []
    list_p_total_final = []
    for comp in lista_delta:
        if vaz_ant != vazao:
            velocidade, profundidade = velocidade_manning(vazao)
            vaz_ant = vazao
        tempo_delta = (delta * 1000) / (velocidade * 86400)

        if index == 0:
            if comp in list_dist_trib:
                index2 = list_dist_trib.index(comp)
                parametros, list_nula = equacoes(
                    lista_parametros, lista_coeficientes,
                    lista_despejos, lista_retirada,
                    delta, index2)
                vazao_trib = parametros[0]
                od_trib = parametros[1]
                dbo5_trib = parametros[2]
                colif_trib = parametros[3]
                norgr_trib = parametros[4]
                namonr_trib = parametros[5]
                nnitritor_trib = parametros[6]
                nnitrator_trib = parametros[7]
                porgr_trib = parametros[8]
                pinorgr_trib = parametros[9]

                od = mistura(od_trib, vazao_trib, od, vazao)
                dbo5 = mistura(dbo5_trib, vazao_trib, dbo5, vazao)
                colif = mistura(colif_trib, vazao_trib, colif, vazao)
                norgr = mistura(norgr_trib, vazao_trib, norgr, vazao)
                namonr = mistura(namonr_trib, vazao_trib, namonr, vazao)
                nnitritor = mistura(nnitritor_trib, vazao_trib,
                                    nnitritor, vazao)
                nnitrator = mistura(nnitrator_trib, vazao_trib,
                                    nnitrator, vazao)
                porgr = mistura(porgr_trib, vazao_trib, porgr, vazao)
                pinorgr = mistura(pinorgr_trib, vazao_trib, pinorgr, vazao)

                vazao += vazao_trib

        if retirada[index]:
            lista_dist_retiradas = lista_retirada[0]
            dist_retiradas = lista_dist_retiradas[index]
            lista_q_retiradas = lista_retirada[1]
            q_retiradas = lista_q_retiradas[index]

            if comp in dist_retiradas:
                index3 = dist_retiradas.index(comp)
                vazao = vazao - q_retiradas[index3]

        if despejo[index]:
            lista_dist_despejos = lista_despejos[0]
            dist_despejos = lista_dist_despejos[index]
            lista_q_despejos = lista_despejos[1]
            q_despejos = lista_q_despejos[index]
            lista_od_despejos = lista_despejos[2]
            od_despejos = lista_od_despejos[index]
            list_dbo5_desp = lista_despejos[3]
            dbo5_desp = list_dbo5_desp[index]
            list_norgr_desp = lista_despejos[4]
            norgr_desp = list_norgr_desp[index]
            list_namonr_desp = lista_despejos[5]
            namonr_desp = list_namonr_desp[index]
            list_enitritor_desp = lista_despejos[6]
            enitritor_desp = list_enitritor_desp[index]
            list_nnitrator_desp = lista_despejos[7]
            nnitrator_desp = list_nnitrator_desp[index]
            list_porgr_desp = lista_despejos[8]
            porgr_desp = list_porgr_desp[index]
            list_pinorgr_desp = lista_despejos[9]
            pinorgr_desp = list_pinorgr_desp[index]
            list_colif_desp = lista_despejos[10]
            colif_desp = list_colif_desp[index]

            if comp in dist_despejos:
                index4 = dist_despejos.index(comp)
                od = mistura(od_despejos[index4], q_despejos[index4],
                             od, vazao)
                dbo5 = mistura(dbo5_desp[index4], q_despejos[index4],
                               dbo5, vazao)
                colif = mistura(colif_desp[index4], q_despejos[index4],
                                colif, vazao)
                norgr = mistura(norgr_desp[index4], q_despejos[index4],
                                norgr, vazao)
                namonr = mistura(namonr_desp[index4], q_despejos[index4],
                                 namonr, vazao)
                nnitritor = mistura(enitritor_desp[index4],
                                    q_despejos[index4], nnitritor, vazao)
                nnitrator = mistura(nnitrator_desp[index4],
                                    q_despejos[index4], nnitrator, vazao)
                porgr = mistura(porgr_desp[index4], q_despejos[index4],
                                porgr, vazao)
                pinorgr = mistura(pinorgr_desp[index4],
                                  q_despejos[index4], pinorgr, vazao)

                vazao += q_despejos[index4]

        # DBO5
        dbo5 += (- ((kd + ks) * dbo5 * tempo_delta)
                 + ((list_lrd[index] / (profundidade * 4)) * tempo_delta))

        # NITROGÊNIO
        if od <= 0:
            fnitr = 0.00001
        else:
            fnitr = 1 - np.exp(1) ** (-list_knitr[index] * od)

        norgr += - (norgr * (kso + koa) * tempo_delta)

        namonr += ((koa * norgr) - (kan * fnitr * snamon)
                   + (snamon / profundidade)) * tempo_delta

        nnitritor += ((kan * fnitr * namonr)
                      - (knn * fnitr * nnitritor)) * tempo_delta

        nnitrator += (knn * fnitr * nnitritor * tempo_delta)

        n_total = norgr + namonr + nnitritor + nnitrator

        # OD
        k2 = k2_eq(list_m, list_n, list_k2_max, list_temperatura, index, vazao)

        reaeracao = k2 * (od_saturacao - od) * tempo_delta

        decomposicao = -(kd * dbo5 * kt * tempo_delta)

        oxid_amonia = -(list_o2namon[index] * namonr
                        * kan * fnitr * tempo_delta)

        oxid_nitrito = -(list_o2nnitri[index] * nnitritor
                         * knn * fnitr * tempo_delta)

        fotossintese = (taxa_fotossintese / profundidade) * tempo_delta

        respiracao = -(taxa_respiracao / profundidade) * tempo_delta

        sedimento = -(taxa_sedimento / profundidade) * tempo_delta

        od = (reaeracao + decomposicao + oxid_amonia + oxid_nitrito
              + fotossintese + respiracao + sedimento)

        if od < 0:
            od = 0

        # FÓSFORO
        porgr += -(porgr * (kspo + koi) * tempo_delta)

        pinorgr += ((koi * porgr) + (spinorg / profundidade)) * tempo_delta

        p_total = porgr + pinorgr

        # COLIFORMES
        colif += -(colif * kb * tempo_delta)

        if index == 0:
            list_qr_final.append(vazao)
            list_od_final.append(od)
            list_dbo5_final.append(dbo5)
            list_colif_final.append(colif)
            list_norgr_final.append(norgr)
            list_namonr_final.append(namonr)
            list_nnitritor_final.append(nnitritor)
            list_nnitrator_final.append(nnitrator)
            list_porgr_final.append(porgr)
            list_pinorgr_final.append(pinorgr)
            list_n_total_final.append(n_total)
            list_p_total_final.append(p_total)

    list_parametros_finais = [vazao, od, dbo5, colif, norgr, namonr, nnitritor,
                              nnitrator, porgr, pinorgr]

    list_final = [lista_delta, list_qr_final, list_od_final, list_dbo5_final,
                  list_colif_final, list_norgr_final, list_namonr_final,
                  list_nnitritor_final, list_nnitrator_final,
                  list_porgr_final, list_pinorgr_final,
                  list_n_total_final, list_p_total_final]
    return list_parametros_finais, list_final


def equacoes_calibragem(
        lista_parametros, lista_coeficientes, lista_despejos,
        lista_retirada, delta, index, k2):

    list_qr = lista_parametros[0]
    list_od = lista_parametros[1]
    list_dbo5 = lista_parametros[2]
    list_temperatura = lista_parametros[3]
    list_altitude = lista_parametros[4]
    list_colif = lista_parametros[5]
    list_norgr = lista_parametros[6]
    list_namonr = lista_parametros[7]
    list_nnitritor = lista_parametros[8]
    list_nnitrator = lista_parametros[9]
    list_porgr = lista_parametros[10]
    list_pinorgr = lista_parametros[11]
    list_dist_trib = lista_parametros[12]
    list_comp = lista_parametros[13]

    list_kso = lista_coeficientes[0]
    kso = list_kso[index] * 1.024 ** (list_temperatura[index] - 20)
    list_koa = lista_coeficientes[1]
    koa = list_koa[index] * 1.047 ** (list_temperatura[index] - 20)
    list_kan = lista_coeficientes[2]
    kan = list_kan[index] * 1.080 ** (list_temperatura[index] - 20)
    list_knn = lista_coeficientes[3]
    knn = list_knn[index] * 1.047 ** (list_temperatura[index] - 20)
    list_o2namon = lista_coeficientes[4]
    list_o2nnitri = lista_coeficientes[5]
    list_knitr = lista_coeficientes[6]
    list_kspo = lista_coeficientes[10]
    kspo = list_kspo[index] * 1.024 ** (list_temperatura[index] - 20)
    list_koi = lista_coeficientes[11]
    koi = list_koi[index] * 1.047 ** (list_temperatura[index] - 20)
    list_kb = lista_coeficientes[12]
    kb = list_kb[index] * 1.07 ** (list_temperatura[index] - 20)
    list_snamon = lista_coeficientes[13]
    snamon = list_snamon[index] * 1.074 ** (list_temperatura[index] - 20)
    list_k1 = lista_coeficientes[14]
    k1 = list_k1[index] * 1.047 ** (list_temperatura[index] - 20)
    kt = 1 / (np.exp(-5 * k1))
    list_kd = lista_coeficientes[15]
    kd = list_kd[index] * 1.047 ** (list_temperatura[index] - 20)
    list_ks = lista_coeficientes[16]
    ks = list_ks[index] * 1.024 ** (list_temperatura[index] - 20)
    list_spinorg = lista_coeficientes[17]
    spinorg = list_spinorg[index] * 1.074 ** (list_temperatura[index] - 20)
    list_fotossintese = lista_coeficientes[18]
    taxa_fotossintese = list_fotossintese[index] * (
        1.047 ** (list_temperatura[index] - 20))
    list_respiracao = lista_coeficientes[19]
    taxa_respiracao = list_respiracao[index] * (
        1.047 ** (list_temperatura[index] - 20))
    list_sedimento = lista_coeficientes[20]
    taxa_sedimento = list_sedimento[index] * (
        1.06 ** (list_temperatura[index] - 20))
    list_lrd = lista_coeficientes[21]

    retirada = lista_retirada[2]
    despejo = lista_despejos[11]

    lista_delta = np.arange(0, list_comp[index], delta)
    vazao = list_qr[index]
    vaz_ant = vazao
    velocidade, profundidade = velocidade_manning(vazao)
    od = list_od[index]
    dbo5 = list_dbo5[index]
    od_saturacao = (1 - (list_altitude[index]/9450)) * (
        14.652 - (4.1022 * (10 ** -list_temperatura[index]))
        + (7.991 * 10 ** (-3) * (list_temperatura[index] ** 2))
        - (7.7774 * 10 ** (-5) * (list_temperatura[index] ** 3)))
    colif = list_colif[index]
    norgr = list_norgr[index]
    namonr = list_namonr[index]
    nnitritor = list_nnitritor[index]
    nnitrator = list_nnitrator[index]
    porgr = list_porgr[index]
    pinorgr = list_pinorgr[index]
    list_qr_final = []
    list_od_final = []
    list_dbo5_final = []
    list_colif_final = []
    list_norgr_final = []
    list_namonr_final = []
    list_nnitritor_final = []
    list_nnitrator_final = []
    list_porgr_final = []
    list_pinorgr_final = []
    list_n_total_final = []
    list_p_total_final = []
    for comp in lista_delta:
        if vaz_ant != vazao:
            velocidade, profundidade = velocidade_manning(vazao)
            vaz_ant = vazao
        tempo_delta = (delta * 1000) / (velocidade * 86400)

        if index == 0:
            if comp in list_dist_trib:
                index2 = list_dist_trib.index(comp)
                parametros, list_nula = equacoes(
                    lista_parametros, lista_coeficientes,
                    lista_despejos, lista_retirada,
                    delta, index2)
                vazao_trib = parametros[0]
                od_trib = parametros[1]
                dbo5_trib = parametros[2]
                colif_trib = parametros[3]
                norgr_trib = parametros[4]
                namonr_trib = parametros[5]
                nnitritor_trib = parametros[6]
                nnitrator_trib = parametros[7]
                porgr_trib = parametros[8]
                pinorgr_trib = parametros[9]

                od = mistura(od_trib, vazao_trib, od, vazao)
                dbo5 = mistura(dbo5_trib, vazao_trib, dbo5, vazao)
                colif = mistura(colif_trib, vazao_trib, colif, vazao)
                norgr = mistura(norgr_trib, vazao_trib, norgr, vazao)
                namonr = mistura(namonr_trib, vazao_trib, namonr, vazao)
                nnitritor = mistura(nnitritor_trib, vazao_trib,
                                    nnitritor, vazao)
                nnitrator = mistura(nnitrator_trib, vazao_trib,
                                    nnitrator, vazao)
                porgr = mistura(porgr_trib, vazao_trib, porgr, vazao)
                pinorgr = mistura(pinorgr_trib, vazao_trib, pinorgr, vazao)

                vazao += vazao_trib

        if retirada[index]:
            lista_dist_retiradas = lista_retirada[0]
            dist_retiradas = lista_dist_retiradas[index]
            lista_q_retiradas = lista_retirada[1]
            q_retiradas = lista_q_retiradas[index]

            if comp in dist_retiradas:
                index3 = dist_retiradas.index(comp)
                vazao = vazao - q_retiradas[index3]

        if despejo[index]:
            lista_dist_despejos = lista_despejos[0]
            dist_despejos = lista_dist_despejos[index]
            lista_q_despejos = lista_despejos[1]
            q_despejos = lista_q_despejos[index]
            lista_od_despejos = lista_despejos[2]
            od_despejos = lista_od_despejos[index]
            list_dbo5_desp = lista_despejos[3]
            dbo5_desp = list_dbo5_desp[index]
            list_norgr_desp = lista_despejos[4]
            norgr_desp = list_norgr_desp[index]
            list_namonr_desp = lista_despejos[5]
            namonr_desp = list_namonr_desp[index]
            list_enitritor_desp = lista_despejos[6]
            enitritor_desp = list_enitritor_desp[index]
            list_nnitrator_desp = lista_despejos[7]
            nnitrator_desp = list_nnitrator_desp[index]
            list_porgr_desp = lista_despejos[8]
            porgr_desp = list_porgr_desp[index]
            list_pinorgr_desp = lista_despejos[9]
            pinorgr_desp = list_pinorgr_desp[index]
            list_colif_desp = lista_despejos[10]
            colif_desp = list_colif_desp[index]

            if comp in dist_despejos:
                index4 = dist_despejos.index(comp)
                od = mistura(od_despejos[index4], q_despejos[index4],
                             od, vazao)
                dbo5 = mistura(dbo5_desp[index4], q_despejos[index4],
                               dbo5, vazao)
                colif = mistura(colif_desp[index4], q_despejos[index4],
                                colif, vazao)
                norgr = mistura(norgr_desp[index4], q_despejos[index4],
                                norgr, vazao)
                namonr = mistura(namonr_desp[index4], q_despejos[index4],
                                 namonr, vazao)
                nnitritor = mistura(enitritor_desp[index4],
                                    q_despejos[index4], nnitritor, vazao)
                nnitrator = mistura(nnitrator_desp[index4],
                                    q_despejos[index4], nnitrator, vazao)
                porgr = mistura(porgr_desp[index4], q_despejos[index4],
                                porgr, vazao)
                pinorgr = mistura(pinorgr_desp[index4],
                                  q_despejos[index4], pinorgr, vazao)

                vazao += q_despejos[index4]

        # DBO5
        dbo5 += (- ((kd + ks) * dbo5 * tempo_delta)
                 + ((list_lrd[index] / (profundidade * 4)) * tempo_delta))

        # NITROGÊNIO
        if od <= 0:
            fnitr = 0.00001
        else:
            fnitr = 1 - np.exp(1) ** (-list_knitr[index] * od)

        norgr += - (norgr * (kso + koa) * tempo_delta)

        namonr += ((koa * norgr) - (kan * fnitr * snamon)
                   + (snamon / profundidade)) * tempo_delta

        nnitritor += ((kan * fnitr * namonr)
                      - (knn * fnitr * nnitritor)) * tempo_delta

        nnitrator += (knn * fnitr * nnitritor * tempo_delta)

        n_total = norgr + namonr + nnitritor + nnitrator

        # OD
        reaeracao = k2 * (od_saturacao - od) * tempo_delta

        decomposicao = -(kd * dbo5 * kt * tempo_delta)

        oxid_amonia = -(list_o2namon[index] * namonr
                        * kan * fnitr * tempo_delta)

        oxid_nitrito = -(list_o2nnitri[index] * nnitritor
                         * knn * fnitr * tempo_delta)

        fotossintese = (taxa_fotossintese / profundidade) * tempo_delta

        respiracao = -(taxa_respiracao / profundidade) * tempo_delta

        sedimento = -(taxa_sedimento / profundidade) * tempo_delta

        od = (reaeracao + decomposicao + oxid_amonia + oxid_nitrito
              + fotossintese + respiracao + sedimento)

        if od < 0:
            od = 0

        # FÓSFORO
        porgr += -(porgr * (kspo + koi) * tempo_delta)

        pinorgr += ((koi * porgr) + (spinorg / profundidade)) * tempo_delta

        p_total = porgr + pinorgr

        # COLIFORMES
        colif += -(colif * kb * tempo_delta)

        if index == 0:
            list_qr_final.append(vazao)
            list_od_final.append(od)
            list_dbo5_final.append(dbo5)
            list_colif_final.append(colif)
            list_norgr_final.append(norgr)
            list_namonr_final.append(namonr)
            list_nnitritor_final.append(nnitritor)
            list_nnitrator_final.append(nnitrator)
            list_porgr_final.append(porgr)
            list_pinorgr_final.append(pinorgr)
            list_n_total_final.append(n_total)
            list_p_total_final.append(p_total)

    list_parametros_finais = [vazao, od, dbo5, colif, norgr, namonr, nnitritor,
                              nnitrator, porgr, pinorgr]

    list_final = [lista_delta, list_qr_final, list_od_final, list_dbo5_final,
                  list_colif_final, list_norgr_final, list_namonr_final,
                  list_nnitritor_final, list_nnitrator_final,
                  list_porgr_final, list_pinorgr_final,
                  list_n_total_final, list_p_total_final]
    return list_parametros_finais, list_final
