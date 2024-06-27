import numpy as np
import pandas as pd
import scipy.optimize as opt
import copy
import streamlit as st

##########################################################################################################
# OBJETOS
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


# Coeficientes               
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


# Resultados finais
class Quanti_Qualitativo:
    def __init__(self, hidraulica, concentracoes, coeficientes, rio):
        self.hidraulica = hidraulica
        self.concentracoes = concentracoes
        self.coeficientes = coeficientes
        self.rio = rio



#########################################################################
def fun_hipotenusa(x1, x2, y1, y2):
    hipotenusa = np.sqrt((x2-x1)**2 + (y2 -y1)**2)
    return hipotenusa


def fun_discr(posterior, anterior, x, parametro_posterior, parametro_anterior):
    if posterior - anterior == 0:
        razao = 1
    else:
        razao = (x - anterior)/(posterior - anterior)
    discret = parametro_anterior + ((parametro_posterior - parametro_anterior) * razao)
    return discret


def lista_hidr(longitude, latitude, altitude, comprimento, discretizacao):
    lista_dist_real = []
    lista_acum = [0]
    acumulado = 0

    if longitude[0] != None:
        for i in range(len(longitude)-1):
            hipotenusa = fun_hipotenusa(longitude[i], longitude[i+1], latitude[i], latitude[i+1])
            acumulado += hipotenusa
            lista_acum.append(acumulado)
            lista_dist_real.append(hipotenusa)

        m_trecho = lista_acum[-1]
        intervalos = list(np.arange(0, (m_trecho + discretizacao), discretizacao))

        lista_hidraulica= []

        for i in range(len(intervalos)):
            for j in range(len(lista_acum) - 1):
                if lista_acum[j] <= intervalos[i] <= lista_acum[j + 1]:
                    long = fun_discr(lista_acum[j + 1], lista_acum[j], intervalos[i],
                                    longitude[j + 1], longitude[j])
                    lat = fun_discr(lista_acum[j + 1], lista_acum[j], intervalos[i],
                                    latitude[j + 1], latitude[j])
                    alt = fun_discr(lista_acum[j + 1], lista_acum[j], intervalos[i],
                                    altitude[j + 1], altitude[j])

            hidraulica = Hidraulica(lat, long, intervalos[i], None, None, None, alt,
                                    None, None, None, None, None, None, None, None)
            lista_hidraulica.append(copy.deepcopy(hidraulica))
    else:
        intervalos = list(np.arange(0, (comprimento[-1] + discretizacao), discretizacao))

        lista_hidraulica= []

        for i in range(len(intervalos)):
            for j in range(len(comprimento) - 1):
                if comprimento[j] <= intervalos[i] <= comprimento[j + 1]:
                    alt = fun_discr(comprimento[j + 1], comprimento[j], intervalos[i],
                                    altitude[j + 1], altitude[j])

            hidraulica = Hidraulica(None, None, intervalos[i], None, None, None, alt,
                                    None, None, None, None, None, None, None, None)
            lista_hidraulica.append(copy.deepcopy(hidraulica))

    # ERRO!!!!!!!!!!!!!!- Inclinação
    for i in range(len(lista_hidraulica)):
        if i != (len(lista_hidraulica) - 1):
            incl = (lista_hidraulica[i].altitude
                    - lista_hidraulica[i+1].altitude)/ discretizacao
            if incl <= 0:
                if i == 0:
                    incl = 0.0001
                else:
                    incl = lista_hidraulica[i - 1].inclinacao
        lista_hidraulica[i].inclinacao = np.abs(incl)
    
    return lista_hidraulica


def func_hidraulica(lista_hidraulica, lista_s_pontual, lista_e_pontual, lista_e_difusa, lista_s_transversal, discretizacao):

    vazao_atual = 0
    lista_final = []
    a_esq = lista_s_transversal[0].ang_esquerdo
    a_dir = lista_s_transversal[0].ang_direito
    l_rio = lista_s_transversal[0].largura_rio
    rug = lista_s_transversal[0].rugosidade_n
    
    for i in range(len(lista_hidraulica)):

        # ENTRADAS E SAÍDAS
        for j in range(len(lista_e_pontual)):
            if lista_hidraulica[i].comprimento == lista_e_pontual[j].comprimento:
                vazao_atual += lista_e_pontual[j].vazao
        if len(lista_s_pontual) > 0:
            for k in range(len(lista_s_pontual)):
                if lista_hidraulica[i].comprimento == lista_s_pontual[k].comprimento:
                    vazao_atual -= lista_s_pontual[k].vazao
        if len(lista_e_difusa) > 0:
            for n in range(len(lista_e_difusa)):
                if lista_e_difusa[n].comprimento_inicial <= lista_hidraulica[i].comprimento < lista_e_difusa[n].comprimento_final:
                    fator_divisor = (lista_e_difusa[n].comprimento_final - lista_e_difusa[n].comprimento_inicial) / discretizacao
                    vazao_atual += (lista_e_difusa[n].vazao / fator_divisor)


        # SECÇÃO TRANSVERSAL
        for m in range(len(lista_s_transversal) - 1):
            if lista_s_transversal[m].comprimento <= lista_hidraulica[i].comprimento <= lista_s_transversal[m + 1].comprimento:
                a_esq = fun_discr(lista_s_transversal[m + 1].comprimento, lista_s_transversal[m].comprimento,
                                lista_hidraulica[i].comprimento, lista_s_transversal[m + 1].ang_esquerdo,
                                lista_s_transversal[m].ang_esquerdo)
                a_dir = fun_discr(lista_s_transversal[m + 1].comprimento, lista_s_transversal[m].comprimento,
                                lista_hidraulica[i].comprimento, lista_s_transversal[m + 1].ang_direito,
                                lista_s_transversal[m].ang_direito)
                l_rio =  fun_discr(lista_s_transversal[m + 1].comprimento, lista_s_transversal[m].comprimento,
                                lista_hidraulica[i].comprimento, lista_s_transversal[m + 1].largura_rio,
                                lista_s_transversal[m].largura_rio)
                rug =  fun_discr(lista_s_transversal[m + 1].comprimento, lista_s_transversal[m].comprimento,
                                lista_hidraulica[i].comprimento, lista_s_transversal[m + 1].rugosidade_n,
                                lista_s_transversal[m].rugosidade_n)
        
        for _ in range(len(lista_s_transversal)):
            funcao_1 = (vazao_atual * rug) / np.sqrt(lista_hidraulica[i].inclinacao)
            funcao_2 = lambda y : (((((2 * l_rio + (y / np.tan(a_esq * np.pi / 180)) + (y / np.tan(a_dir * np.pi / 180))) * (y / 2)) ** (5/3)) / (
                ((y / np.sin(a_esq * np.pi / 180)) + (y / np.sin(a_dir * np.pi / 180)) + l_rio) ** (2/3))) - funcao_1)
            prof = opt.bisect(funcao_2, 0,500)
            nivel_dagua = lista_hidraulica[i].altitude + prof
            area = ((2 * l_rio + (prof / np.tan(a_esq * np.pi / 180)) + (prof / np.tan(a_dir * np.pi / 180))) * (prof / 2))
            veloc = vazao_atual / area
            tensao_c = 9810 * lista_hidraulica[i].inclinacao * (area / (
                (prof / np.sin(a_esq * np.pi / 180)) + (prof / np.sin(a_dir * np.pi / 180)) + l_rio))
            froude = veloc / (np.sqrt(9.81 * prof))

        lista_hidraulica[i].vazao = vazao_atual
        lista_hidraulica[i].ang_esquerdo = a_esq
        lista_hidraulica[i].ang_direito = a_dir
        lista_hidraulica[i].rugosidade_n = rug
        lista_hidraulica[i].largura_rio = l_rio
        lista_hidraulica[i].profundidade = prof
        lista_hidraulica[i].nivel_dagua = nivel_dagua
        lista_hidraulica[i].velocidade = veloc
        lista_hidraulica[i].tensao_c = tensao_c
        lista_hidraulica[i].froude = froude

        final = Quanti_Qualitativo(lista_hidraulica[i], None, None, None)
        lista_final.append(copy.deepcopy(final))
    
    return lista_final


def k2(hidraulica):

    if 0.1 <= hidraulica.profundidade < 4 and 0.05 <= hidraulica.velocidade < 1.6:
        if 0.6 <= hidraulica.profundidade < 4 and 0.05 <= hidraulica.velocidade < 0.8:
            k_2 = 3.73 * (hidraulica.velocidade ** 0.5) * (hidraulica.profundidade ** -1.5)
        elif 0.6 <= hidraulica.profundidade < 4 and 0.8 <= hidraulica.velocidade < 1.6:
            k_2 = 5 * (hidraulica.velocidade ** 0.97) * (hidraulica.profundidade ** -1.67)
        else:
            k_2 = 5.3 * (hidraulica.velocidade ** 0.67) * (hidraulica.profundidade ** -1.85)
    elif 0.03 <= hidraulica.vazao <= 8.5:
        if 0.03 <= hidraulica.vazao < 0.3:
            k_2 = 31.6 * hidraulica.velocidade * hidraulica.inclinacao
        else:
            k_2 = 15.4 * hidraulica.velocidade * hidraulica.inclinacao
    else:
        k_2 = 20.74 * (hidraulica.vazao ** -0.42)

    return k_2


def mistura(parametro, e_paramentro, vazao, e_vazao):
    conc = ((parametro * (vazao - e_vazao)) + (e_paramentro * e_vazao)) / vazao
    return conc


def od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, od_saturacao, anaerobiose):
    
    if anaerobiose:
        conc_od = 0
    
    else:
        k_t = 1 / (1 - np.exp(-5 * (coeficientes.k_1 * (1.047 ** (coeficientes.temperatura - 20)))))
        k_r = (coeficientes.k_d * (1.047 ** (coeficientes.temperatura - 20))
               ) + (coeficientes.k_s * (1.024 ** (coeficientes.temperatura - 20)))
        conc = (coeficientes.k_2 * (1.024 ** (coeficientes.temperatura - 20)) * (od_saturacao - concentracoes.conc_od)
                ) - (k_r * k_t * concentracoes.conc_dbo
                     ) - (coeficientes.r_o2_amon * f_nitr * concentracoes.conc_n_amon * coeficientes.k_an * (1.08 ** (coeficientes.temperatura - 20))
                          ) - (coeficientes.s_d * (1.06 ** (coeficientes.temperatura - 20)) / hidraulica.profundidade)
        conc_od = concentracoes.conc_od + (tempo_delta * conc)

        if conc_od <= 0:
            anaerobiose = True
            conc_od = 0
    return conc_od, anaerobiose


def dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose):

    od_saturacao = (1 - (hidraulica.altitude/9450)) * (
        14.652 - (4.1022 * (10 ** -1) * coeficientes.temperatura)
        + (7.991 * (10 ** -3) * (coeficientes.temperatura ** 2))
        - (7.7774 * (10 ** -5) * (coeficientes.temperatura ** 3)))

    k_r = (coeficientes.k_d * (1.047 ** (coeficientes.temperatura - 20))
           ) + (coeficientes.k_s * (1.024 ** (coeficientes.temperatura - 20)))
    
    conc = (- k_r * concentracoes.conc_dbo) + (coeficientes.l_rd / (hidraulica.profundidade * hidraulica.largura_rio))
    conc_dbo_aerobio = concentracoes.conc_dbo + (tempo_delta * conc)

    if anaerobiose:
        conc_ana = - (coeficientes.k_2 * (1.024 ** (coeficientes.temperatura - 20)) * od_saturacao)
        conc_dbo_anaerobio = concentracoes.conc_dbo + (tempo_delta * conc_ana)
        if abs(conc_dbo_anaerobio - conc_dbo_aerobio) <= 0.001:
            anaerobiose = False
            conc_dbo = conc_dbo_aerobio
        else:
            conc_dbo = conc_dbo_anaerobio
    else:
        conc_dbo = conc_dbo_aerobio

    return conc_dbo, od_saturacao, anaerobiose


def no(tempo_delta, coeficientes, concentracoes):
    conc = - ((coeficientes.k_oa * (1.047 ** (coeficientes.temperatura - 20))
               ) + (coeficientes.k_so * (1.024568 ** (coeficientes.temperatura - 20)))) * concentracoes.conc_no
    conc_no = concentracoes.conc_no + (tempo_delta * conc)
    return conc_no


def n_amon(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr):
    conc = (coeficientes.k_oa * (1.047 ** (coeficientes.temperatura - 20)) * concentracoes.conc_no
               ) - (f_nitr * concentracoes.conc_n_amon *coeficientes.k_an * (1.08 ** (coeficientes.temperatura - 20))
                   ) + (coeficientes.s_amon * (1.074 ** (coeficientes.temperatura - 20)) / hidraulica.profundidade)
    conc_n_amon = concentracoes.conc_n_amon + (tempo_delta * conc)
    return conc_n_amon


def nitrito(tempo_delta, coeficientes, concentracoes, f_nitr):
    conc = (f_nitr * concentracoes.conc_n_amon * coeficientes.k_an * (1.08 ** (coeficientes.temperatura - 20))
            ) - (f_nitr * concentracoes.conc_nitrito * coeficientes.k_nn * (1.047 ** (coeficientes.temperatura - 20)))
    conc_nitrito = concentracoes.conc_nitrito + (tempo_delta * conc)
    return conc_nitrito


def nitrato(tempo_delta, coeficientes, concentracoes, f_nitr):
    conc = (f_nitr * coeficientes.k_nn * concentracoes.conc_nitrito * (1.047 ** (coeficientes.temperatura - 20)))
    conc_nitrato = concentracoes.conc_nitrato + (tempo_delta * conc)
    return conc_nitrato


def p_org(tempo_delta, coeficientes, concentracoes):
    conc = - ((coeficientes.k_oi * (1.047 ** (coeficientes.temperatura - 20))
               ) + (coeficientes.k_spo * (1.024 ** (coeficientes.temperatura - 20)))) * concentracoes.conc_p_org 
    conc_p_org = concentracoes.conc_p_org + (tempo_delta * conc)
    return conc_p_org


def p_inorg(tempo_delta, coeficientes, concentracoes, hidraulica):
    conc = (coeficientes.k_oi * (1.047 ** (coeficientes.temperatura - 20)) * concentracoes.conc_p_inorg
            ) + (coeficientes.s_pinorg * (1.074 ** (coeficientes.temperatura - 20)) / hidraulica.profundidade)
    conc_p_inorg = concentracoes.conc_p_inorg + (tempo_delta * conc)
    return conc_p_inorg


def e_coli(tempo_delta, coeficientes, concentracoes):
    conc = - coeficientes.k_b * concentracoes.conc_e_coli * (1.07 ** (coeficientes.temperatura - 20))
    conc_e_coli = concentracoes.conc_e_coli + (tempo_delta * conc)
    return conc_e_coli


def modelagem(lista_final, lista_e_coeficientes, lista_s_pontual, lista_e_pontual,
              lista_e_difusa, rio, discretizacao, lista_modelagem):
    anaerobiose = False
    vazao = 0
    concentracoes = Concentracoes(None, None, None, None, None, None, None, None, None, None)
    coeficientes = Coeficientes(None, None, None, None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None, None, None, None)

    for i in range(len(lista_final)):
        hidraulica = lista_final[i].hidraulica
        
        for j in range(len(lista_e_coeficientes)):
            atual = lista_e_coeficientes[j]
            if atual.comprimento == hidraulica.comprimento:
                k_2_calculavel = atual.coeficientes.k_2_calculavel
                k_2_max = atual.coeficientes.k_2_max
                if lista_modelagem[0]:
                    if k_2_calculavel:
                        k_2 = k2(lista_final[0].hidraulica)
                        if k_2 > atual.coeficientes.k_2_max:
                            k_2 = atual.coeficientes.k_2_max
                    else:
                        k_2 = atual.coeficientes.k_2
                else:
                    k_2 = atual.coeficientes.k_2
                temperatura = atual.coeficientes.temperatura
                k_1 = atual.coeficientes.k_1
                s_d = atual.coeficientes.s_d
                k_d = atual.coeficientes.k_d
                k_s = atual.coeficientes.k_s
                l_rd = atual.coeficientes.l_rd
                k_so = atual.coeficientes.k_so
                k_oa = atual.coeficientes.k_oa
                k_an = atual.coeficientes.k_an
                k_nn = atual.coeficientes.k_nn
                s_amon = atual.coeficientes.s_amon
                k_spo = atual.coeficientes.k_spo
                k_oi = atual.coeficientes.k_oi
                k_b = atual.coeficientes.k_b
                r_o2_amon = atual.coeficientes.r_o2_amon
                k_nit_od = atual.coeficientes.k_nit_od
                s_pinorg = atual.coeficientes.s_pinorg

        coeficientes.k_2 = k_2
        coeficientes.k_2_calculavel = k_2_calculavel
        coeficientes.k_2_max = k_2_max
        coeficientes.temperatura = temperatura
        coeficientes.k_1 = k_1
        coeficientes.s_d = s_d
        coeficientes.k_d = k_d
        coeficientes.k_s = k_s
        coeficientes.l_rd = l_rd
        coeficientes.k_so = k_so
        coeficientes.k_oa = k_oa
        coeficientes.k_an = k_an
        coeficientes.k_nn = k_nn
        coeficientes.s_amon = s_amon
        coeficientes.k_spo = k_spo
        coeficientes.k_oi = k_oi
        coeficientes.k_b = k_b
        coeficientes.r_o2_amon = r_o2_amon
        coeficientes.k_nit_od = k_nit_od
        coeficientes.s_pinorg = s_pinorg
        
        if i == 0:
            concentracoes = lista_e_pontual[0].concentracoes

        else:
            tempo_delta = discretizacao / (hidraulica.velocidade * 86400)
            
            if lista_modelagem[3]:
                f_nitr = 1 - np.exp(1) ** (- coeficientes.k_nit_od * concentracoes.conc_od)
            
            if lista_modelagem[0] or lista_modelagem[2]:
                concentracoes.conc_dbo, od_saturacao, anaerobiose = dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose)
            if lista_modelagem[3]:
                concentracoes.conc_no = no(tempo_delta, coeficientes, concentracoes)
                concentracoes.conc_n_amon = n_amon(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr)
                concentracoes.conc_nitrito = nitrito(tempo_delta, coeficientes, concentracoes, f_nitr)
                concentracoes.conc_nitrato = nitrato(tempo_delta, coeficientes, concentracoes, f_nitr)
            if lista_modelagem[0]:
                concentracoes.conc_od, anaerobiose = od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, od_saturacao, anaerobiose)
            if lista_modelagem[4]:
                concentracoes.conc_p_org = p_org(tempo_delta, coeficientes, concentracoes)
                concentracoes.conc_p_inorg = p_inorg(tempo_delta, coeficientes, concentracoes, hidraulica)
                concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
            if lista_modelagem[5]:
                concentracoes.conc_e_coli = e_coli(tempo_delta, coeficientes, concentracoes)
          
        for k in range(len(lista_e_pontual)):
            ep_concetracoes = lista_e_pontual[k].concentracoes
            if hidraulica.comprimento == lista_e_pontual[k].comprimento:
                vazao += lista_e_pontual[k].vazao
                if lista_modelagem[0]:
                    concentracoes.conc_od = mistura(concentracoes.conc_od, ep_concetracoes.conc_od, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem[0] or lista_modelagem[2]:
                    concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ep_concetracoes.conc_dbo, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem[3]:
                    concentracoes.conc_no = mistura(concentracoes.conc_no, ep_concetracoes.conc_no, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ep_concetracoes.conc_n_amon, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ep_concetracoes.conc_nitrito, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem[4]:
                    concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ep_concetracoes.conc_p_org, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ep_concetracoes.conc_p_inorg, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                if lista_modelagem[5]:
                    concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ep_concetracoes.conc_e_coli, vazao, lista_e_pontual[k].vazao)

        if len(lista_e_difusa) > 0 :
            for n in range(len(lista_e_difusa)):
                ed_concetracoes = lista_e_difusa[n].concentracoes
                if lista_e_difusa[n].comprimento_inicial <= hidraulica.comprimento <= lista_e_difusa[n].comprimento_final:

                    vazao_difusa = (lista_e_difusa[n].vazao *  discretizacao
                                    ) / (lista_e_difusa[n].comprimento_final - lista_e_difusa[n].comprimento_inicial)
                    vazao += vazao_difusa

                    if lista_modelagem[0]:
                        concentracoes.conc_od = mistura(concentracoes.conc_od, ed_concetracoes.conc_od, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem[0] or lista_modelagem[2]:
                        concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ed_concetracoes.conc_dbo, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem[3]:
                        concentracoes.conc_no = mistura(concentracoes.conc_no, ed_concetracoes.conc_no, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ed_concetracoes.conc_n_amon, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ed_concetracoes.conc_nitrito, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem[4]:
                        concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ed_concetracoes.conc_p_org, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ed_concetracoes.conc_p_inorg, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                    if lista_modelagem[5]:
                        concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ed_concetracoes.conc_e_coli, hidraulica.vazao, vazao_difusa)
    
        if len(lista_s_pontual) > 0 :
            for p in range(len(lista_s_pontual)):
                    if hidraulica.comprimento == lista_s_pontual[p].comprimento:
                        vazao -= lista_s_pontual[p].vazao
 
        lista_final[i].concentracoes = copy.deepcopy(concentracoes)
        lista_final[i].coeficientes = copy.deepcopy(coeficientes)
        lista_final[i].rio = rio
    return lista_final

    
def modelagem_Final(lista_rio, ponto_af, lista_modelagem):
    lista_afluente = []
    lista_completa_final = []
    for i in range(len(lista_rio)):
        dados = lista_rio[i]
        if dados.rio != 0:
            lista_hidr_model = func_hidraulica(dados.lista_hidraulica, dados.lista_s_pontual,
                                               dados.lista_e_pontual, dados.lista_e_difusa,
                                               dados.lista_s_transversal, dados.discretizacao)
            lista_final = modelagem(lista_hidr_model, dados.lista_e_coeficientes, dados.lista_s_pontual,
                                    dados.lista_e_pontual, dados.lista_e_difusa, dados.rio,
                                    dados.discretizacao, lista_modelagem)
            afluente = EntradaPontual(ponto_af[i][1], ponto_af[i][2],
                                    ponto_af[i][3], lista_final[-1].concentracoes,
                                    lista_final[-1].hidraulica.vazao, ponto_af[i][0], lista_final[-1].rio)
            lista_afluente.append(copy.deepcopy(afluente))
        else:
            if len(lista_rio) > 1:
                for j in range(len(lista_afluente)):
                    dist_ant = 10 ** 50
                    if str(lista_afluente[j].latitude) != 'nan':
                        for k in range(len(dados.lista_hidraulica)):
                            distancia = fun_hipotenusa(lista_afluente[j].latitude, dados.lista_hidraulica[k].latitude,
                                                       lista_afluente[j].longitude, dados.lista_hidraulica[k].longitude)
                            if distancia <= dist_ant:
                                comp = dados.lista_hidraulica[k].comprimento
                                dist_ant = distancia
                    else:
                        for k in range(len(dados.lista_hidraulica)):
                            distancia = abs(lista_afluente[j].comprimento - dados.lista_hidraulica[k].comprimento)
                            if distancia <= dist_ant:
                                comp = dados.lista_hidraulica[k].comprimento
                                dist_ant = distancia
                lista_afluente[j].comprimento = comp
                add = dados.lista_e_pontual
                add.append(copy.deepcopy(lista_afluente[j]))
            else:
                add = dados.lista_e_pontual
            lista_hidr_model = func_hidraulica(dados.lista_hidraulica, dados.lista_s_pontual,
                                               add, dados.lista_e_difusa,
                                               dados.lista_s_transversal, dados.discretizacao)
            lista_final = modelagem(lista_hidr_model, dados.lista_e_coeficientes, dados.lista_s_pontual,
                                    add, dados.lista_e_difusa, dados.rio,
                                    dados.discretizacao, lista_modelagem)
        lista_completa_final.append(lista_final)
    return lista_completa_final, add

