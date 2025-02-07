import numpy as np
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
        self.vazao = vazao
        self.descricao = descricao
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
        lat = [None]
        long = [None]
        lista_hidraulica= []

        for i in range(len(intervalos)):
            for j in range(len(comprimento) - 1):
                if comprimento[j] <= intervalos[i] <= comprimento[j + 1]:
                    alt = fun_discr(comprimento[j + 1], comprimento[j], intervalos[i],
                                    altitude[j + 1], altitude[j])

            hidraulica = Hidraulica(None, None, intervalos[i], None, None, None, alt,
                                    None, None, None, None, None, None, None, None)
            lista_hidraulica.append(copy.deepcopy(hidraulica))

    # Inclinação
    for i in range(len(lista_hidraulica)):
        if i != (len(lista_hidraulica) - 1):
            incl = (lista_hidraulica[i].altitude
                    - lista_hidraulica[i+1].altitude)/ discretizacao
            if incl <= 0:
                if i == 0:
                    incl = 0.00001
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
            list_profundidade = []
            for iq in range(len(vazao_atual)):
                funcao_1 = (vazao_atual[iq] * rug) / np.sqrt(lista_hidraulica[i].inclinacao)
                funcao_2 = lambda y : (((((2 * l_rio + (y / np.tan(a_esq * np.pi / 180)) + (y / np.tan(a_dir * np.pi / 180))) * (y / 2)) ** (5/3)) / (
                    ((y / np.sin(a_esq * np.pi / 180)) + (y / np.sin(a_dir * np.pi / 180)) + l_rio) ** (2/3))) - funcao_1)
                prof = opt.bisect(funcao_2, 0,500)
                list_profundidade.append(prof)
            
            list_profundidade = np.array(list_profundidade)
            nivel_dagua = lista_hidraulica[i].altitude + list_profundidade
            area = ((2 * l_rio + (list_profundidade / np.tan(a_esq * np.pi / 180)) + (list_profundidade / np.tan(a_dir * np.pi / 180))) * (list_profundidade / 2))
            veloc = vazao_atual / area
            tensao_c = 9810 * lista_hidraulica[i].inclinacao * (area / (
                (list_profundidade / np.sin(a_esq * np.pi / 180)) + (list_profundidade / np.sin(a_dir * np.pi / 180)) + l_rio))
            froude = veloc / (np.sqrt(9.81 * list_profundidade))

        lista_hidraulica[i].vazao = vazao_atual
        lista_hidraulica[i].ang_esquerdo = a_esq
        lista_hidraulica[i].ang_direito = a_dir
        lista_hidraulica[i].rugosidade_n = rug
        lista_hidraulica[i].largura_rio = l_rio
        lista_hidraulica[i].profundidade = list_profundidade
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
            k_2 = 31.6 * hidraulica.velocidade * hidraulica.inclinacao * 1000
        else:
            k_2 = 15.4 * hidraulica.velocidade * hidraulica.inclinacao * 1000
    else:
        k_2 = 20.74 * (hidraulica.vazao ** -0.42)
    return k_2


def mistura(parametro, e_paramentro, vazao, e_vazao):
    conc = ((parametro * (vazao - e_vazao)) + (e_paramentro * e_vazao)) / vazao
    return conc


def od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, anaerobiose, mod_n):

    od_saturacao = (1 - (hidraulica.altitude/9450)) * (
        14.652 - (4.1022 * (10 ** -1) * coeficientes.temperatura)
        + (7.991 * (10 ** -3) * (coeficientes.temperatura ** 2))
        - (7.7774 * (10 ** -5) * (coeficientes.temperatura ** 3)))
    
    lista_c_od = []
    for iod in range(len(anaerobiose)):
        
        if anaerobiose[iod]:
            conc_od = 0
        
        else:
            k_t = 1 / (1 - np.exp(-5 * (coeficientes.k_1[iod] * (1.047 ** (coeficientes.temperatura[iod] - 20)))))

            reac = ((coeficientes.k_2[iod] * (1.024 ** (coeficientes.temperatura[iod] - 20)) * (od_saturacao[iod] - concentracoes.conc_od[iod]) * tempo_delta[iod]))
            dbo_carb = (- ((coeficientes.k_d[iod] * (1.047 ** (coeficientes.temperatura[iod] - 20))) * k_t * concentracoes.conc_dbo[iod] * tempo_delta[iod]))
            carga_int = (- (coeficientes.s_d[iod] * (1.06 ** (coeficientes.temperatura[iod] - 20)) / hidraulica.profundidade[iod]) * (tempo_delta[iod]))

            if mod_n:
                oxi_am = (- (coeficientes.r_o2_amon[iod] * f_nitr[iod] * concentracoes.conc_n_amon[iod] * coeficientes.k_an[iod] * (1.08 ** (coeficientes.temperatura[iod] - 20)) * tempo_delta[iod]))
            
            else:
                oxi_am = 0

            conc_od = concentracoes.conc_od[iod] + (reac + dbo_carb + carga_int + oxi_am)
            if conc_od <= 0:
                anaerobiose[iod] = True
                conc_od = 0
        lista_c_od.append(conc_od)
    lista_c_od = np.array(lista_c_od)
        
    return lista_c_od, od_saturacao, anaerobiose


def dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose, od_saturacao):

    
    k_r = (coeficientes.k_d * (1.047 ** (coeficientes.temperatura - 20))
           ) + (coeficientes.k_s * (1.024 ** (coeficientes.temperatura - 20)))
    
    dbo5 = (- k_r * concentracoes.conc_dbo * tempo_delta)
    carg_inte = (coeficientes.l_rd / (hidraulica.profundidade * hidraulica.largura_rio)) * tempo_delta

    conc_dbo_aerobio = concentracoes.conc_dbo + dbo5 + carg_inte
    lista_c_dbo = []
    for idbo in range(len(anaerobiose)):
        if anaerobiose[idbo]:
            conc_ana = - (coeficientes.k_2[idbo] * (1.024 ** (coeficientes.temperatura[idbo] - 20)) * od_saturacao[idbo])
            conc_dbo_anaerobio = concentracoes.conc_dbo[idbo] + (tempo_delta[idbo] * conc_ana)

            if abs(conc_dbo_anaerobio - conc_dbo_aerobio[idbo]) <= 0.001:
                anaerobiose[idbo] = False
                conc_dbo = conc_dbo_aerobio[idbo]
            else:
                conc_dbo = conc_dbo_anaerobio
        else:
            conc_dbo = conc_dbo_aerobio[idbo]
            
        lista_c_dbo.append(conc_dbo)
    lista_c_dbo = np.array(lista_c_dbo)
    

    return lista_c_dbo, anaerobiose


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
    conc = (coeficientes.k_oi * (1.047 ** (coeficientes.temperatura - 20)) * concentracoes.conc_p_org
            ) + (coeficientes.s_pinorg * (1.074 ** (coeficientes.temperatura - 20)) / hidraulica.profundidade)
    conc_p_inorg = concentracoes.conc_p_inorg + (tempo_delta * conc)
    return conc_p_inorg


def e_coli(tempo_delta, coeficientes, concentracoes):
    conc = coeficientes.k_b * concentracoes.conc_e_coli * (1.07 ** (coeficientes.temperatura - 20)) * tempo_delta
    conc_e_coli = concentracoes.conc_e_coli - conc
    return conc_e_coli


def modelagem(lista_final, lista_e_coeficientes, lista_s_pontual, lista_e_pontual,
              lista_e_difusa, rio, discretizacao, lista_modelagem):
    anaerobiose = [False] * len(lista_e_pontual[0].vazao)
    vazao = 0
    coeficientes = Coeficientes(None, None, None, None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None, None, None, None)

    for i in range(len(lista_final)):
        hidraulica = lista_final[i].hidraulica
        
        for j in range(len(lista_e_coeficientes)):
            atual = lista_e_coeficientes[j]
            if atual.comprimento == hidraulica.comprimento:
                k_2_calculavel = atual.coeficientes.k_2_calculavel
                k_2_max = atual.coeficientes.k_2_max
                if lista_modelagem['m_od'] == True and k_2_calculavel == True:
                    k_2 = np.array(k2(lista_final[0].hidraulica))
                    k_2 = np.where(k_2 > atual.coeficientes.k_2_max, atual.coeficientes.k_2_max, k_2)
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
            concentracoes = copy.deepcopy(lista_e_pontual[0].concentracoes)


        for k in range(len(lista_e_pontual)):
            ep_concetracoes = lista_e_pontual[k].concentracoes
            if hidraulica.comprimento == lista_e_pontual[k].comprimento:
                vazao += lista_e_pontual[k].vazao
                if lista_modelagem['m_od']:
                    concentracoes.conc_od = mistura(concentracoes.conc_od, ep_concetracoes.conc_od, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_od']:
                    concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ep_concetracoes.conc_dbo, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_n']:
                    concentracoes.conc_no = mistura(concentracoes.conc_no, ep_concetracoes.conc_no, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ep_concetracoes.conc_n_amon, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ep_concetracoes.conc_nitrito, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_p']:
                    concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ep_concetracoes.conc_p_org, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ep_concetracoes.conc_p_inorg, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                if lista_modelagem['m_c']:
                    concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ep_concetracoes.conc_e_coli, vazao, lista_e_pontual[k].vazao)

        if len(lista_e_difusa) > 0 :
            for n in range(len(lista_e_difusa)):
                ed_concetracoes = lista_e_difusa[n].concentracoes
                if lista_e_difusa[n].comprimento_inicial <= hidraulica.comprimento <= lista_e_difusa[n].comprimento_final:

                    vazao_difusa = (lista_e_difusa[n].vazao *  discretizacao
                                    ) / (lista_e_difusa[n].comprimento_final - lista_e_difusa[n].comprimento_inicial)
                    vazao += vazao_difusa

                    if lista_modelagem['m_od']:
                        concentracoes.conc_od = mistura(concentracoes.conc_od, ed_concetracoes.conc_od, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_od']:
                        concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ed_concetracoes.conc_dbo, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_n']:
                        concentracoes.conc_no = mistura(concentracoes.conc_no, ed_concetracoes.conc_no, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ed_concetracoes.conc_n_amon, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ed_concetracoes.conc_nitrito, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_p']:
                        concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ed_concetracoes.conc_p_org, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ed_concetracoes.conc_p_inorg, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                    if lista_modelagem['m_c']:
                        concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ed_concetracoes.conc_e_coli, hidraulica.vazao, vazao_difusa)
            

        if len(lista_s_pontual) > 0 :
            for p in range(len(lista_s_pontual)):
                    if hidraulica.comprimento == lista_s_pontual[p].comprimento:
                        vazao -= lista_s_pontual[p].vazao
        

        tempo_delta = discretizacao / (hidraulica.velocidade * 86400)
        
        if lista_modelagem['m_n']:
            f_nitr = 1 - np.exp(1) ** (- coeficientes.k_nit_od * concentracoes.conc_od)
        else:
            f_nitr = 0 * concentracoes.conc_od
        
        if lista_modelagem['m_od']:
            concentracoes.conc_od, od_saturacao, anaerobiose = od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, anaerobiose, lista_modelagem['m_n'])
        if lista_modelagem['m_od']:
            concentracoes.conc_dbo, anaerobiose = dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose, od_saturacao)
        if lista_modelagem['m_n']:
            concentracoes.conc_no = no(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_n_amon = n_amon(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr)
            concentracoes.conc_nitrito = nitrito(tempo_delta, coeficientes, concentracoes, f_nitr)
            concentracoes.conc_nitrato = nitrato(tempo_delta, coeficientes, concentracoes, f_nitr)
        if lista_modelagem['m_p']:
            concentracoes.conc_p_org = p_org(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_p_inorg = p_inorg(tempo_delta, coeficientes, concentracoes, hidraulica)
            concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
        if lista_modelagem['m_c']:
            concentracoes.conc_e_coli = e_coli(tempo_delta, coeficientes, concentracoes)
          
 
        lista_final[i].concentracoes = copy.deepcopy(concentracoes)
        lista_final[i].coeficientes = copy.deepcopy(coeficientes)
        lista_final[i].rio = rio
    return lista_final


def menor_dist(list_lat, list_long, list_comp, lat_af, long_af, comp_af):
    dist_ant = 10 ** 50

    for k in range(len(list_lat)):
        
        if str(lat_af) != 'None' and str(lat_af) != 'nan':
            distancia = fun_hipotenusa(lat_af, list_lat[k],
                                        long_af, list_long[k])
        else:
            distancia = abs(comp_af - list_comp[k])
        if distancia <= dist_ant:
            comp = list_comp[k]
            dist_ant = distancia
    
    return comp


def menor_dist2(dados_desague, lat_af, long_af, comp_af):
    dist_ant = 10 ** 50

    for k in range(len(dados_desague.lista_hidraulica)):
        if str(lat_af) != 'None' and str(lat_af) != 'nan':
            distancia = fun_hipotenusa(lat_af, dados_desague.lista_hidraulica[k].latitude,
                                        long_af, dados_desague.lista_hidraulica[k].longitude)
        else:
            distancia = abs(comp_af - dados_desague.lista_hidraulica[k].comprimento)
        if distancia <= dist_ant:
            comp = dados_desague.lista_hidraulica[k].comprimento
            dist_ant = distancia
    
    return comp


def modelagem_Final(lista_rio, ponto_af, lista_modelagem,
                    ordem_desague, ordem_modelagem):
    
    lista_completa_final = []
    for ior in ordem_modelagem:
        dados = lista_rio[ior]
        lista_hidr_model = func_hidraulica(dados.lista_hidraulica, dados.lista_s_pontual,
                                            dados.lista_e_pontual, dados.lista_e_difusa,
                                            dados.lista_s_transversal, dados.discretizacao)
        
        lista_final = modelagem(lista_hidr_model, dados.lista_e_coeficientes, dados.lista_s_pontual,
                                dados.lista_e_pontual, dados.lista_e_difusa, dados.rio,
                                dados.discretizacao, lista_modelagem)
        
        
        if ior != 0:
            comp = menor_dist2(lista_rio[ordem_desague[ior - 1]], ponto_af[ior - 1][1],
                               ponto_af[ior - 1][2], ponto_af[ior - 1][3])

            afluente = EntradaPontual(ponto_af[ior - 1][1], ponto_af[ior - 1][2],
                                      comp, lista_final[-1].concentracoes,
                                      lista_final[-1].hidraulica.vazao, ponto_af[ior - 1][0], lista_final[-1].rio)
            
            lista_rio[ordem_desague[ior - 1]].lista_e_pontual.append(copy.deepcopy(afluente))

        lista_completa_final.append(copy.deepcopy(lista_final))
    return lista_completa_final, lista_rio[0].lista_e_pontual


################################################################################################################


def cb_od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, anaerobiose, mod_n):

    od_saturacao = (1 - (hidraulica.altitude/9450)) * (
        14.652 - (4.1022 * (10 ** -1) * coeficientes.temperatura)
        + (7.991 * (10 ** -3) * (coeficientes.temperatura ** 2))
        - (7.7774 * (10 ** -5) * (coeficientes.temperatura ** 3)))
    
    lista_c_od = []
    for iod in range(len(anaerobiose)):
        
        if anaerobiose[iod]:
            conc_od = 0
        
        else:
            k_t = 1 / (1 - np.exp(-5 * (coeficientes.k_1 * (1.047 ** (coeficientes.temperatura - 20)))))
            
            reac = ((coeficientes.k_2 * (1.024 ** (coeficientes.temperatura - 20)) * (od_saturacao - concentracoes.conc_od[iod]) * tempo_delta[iod]))
            dbo_carb = (- ((coeficientes.k_d * (1.047 ** (coeficientes.temperatura - 20))) * k_t * concentracoes.conc_dbo[iod] * tempo_delta[iod]))
            carga_int = (- (coeficientes.s_d * (1.06 ** (coeficientes.temperatura - 20)) / hidraulica.profundidade[iod]) * (tempo_delta[iod]))

            if mod_n:
                oxi_am = (- (coeficientes.r_o2_amon * f_nitr[iod] * concentracoes.conc_n_amon[iod] * coeficientes.k_an * (1.08 ** (coeficientes.temperatura - 20)) * tempo_delta[iod]))
            
            else:
                oxi_am = 0

            conc_od = concentracoes.conc_od[iod] + (reac + dbo_carb + carga_int + oxi_am)

            if conc_od <= 0:
                anaerobiose[iod] = True
                conc_od = 0
        lista_c_od.append(conc_od)
    lista_c_od = np.array(lista_c_od)
    
        
    return lista_c_od, od_saturacao, anaerobiose


def cb_dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose, od_saturacao):
    
    k_r = (coeficientes.k_d * (1.047 ** (coeficientes.temperatura - 20))
           ) + (coeficientes.k_s * (1.024 ** (coeficientes.temperatura - 20)))
    
    dbo5 = (- k_r * concentracoes.conc_dbo * tempo_delta)
    carg_inte = (coeficientes.l_rd / (hidraulica.profundidade * hidraulica.largura_rio)) * tempo_delta

    conc_dbo_aerobio = concentracoes.conc_dbo + dbo5 + carg_inte
    lista_c_dbo = []
    for idbo in range(len(anaerobiose)):
        if anaerobiose[idbo]:
            conc_ana = - (coeficientes.k_2 * (1.024 ** (coeficientes.temperatura - 20)) * od_saturacao)
            conc_dbo_anaerobio = concentracoes.conc_dbo[idbo] + (tempo_delta[idbo] * conc_ana)
            if abs(conc_dbo_anaerobio - conc_dbo_aerobio[idbo]) <= 0.001:
                anaerobiose[idbo] = False
                conc_dbo = conc_dbo_aerobio[idbo]
            else:
                conc_dbo = conc_dbo_anaerobio
        else:
            conc_dbo = conc_dbo_aerobio[idbo]
            
        lista_c_dbo.append(conc_dbo)
    lista_c_dbo = np.array(lista_c_dbo)

    return lista_c_dbo, anaerobiose


def cb_no(tempo_delta, coeficientes, concentracoes):
    conc = - ((coeficientes.k_oa * (1.047 ** (coeficientes.temperatura - 20))
               ) + (coeficientes.k_so * (1.024568 ** (coeficientes.temperatura - 20)))) * concentracoes.conc_no
    conc_no = concentracoes.conc_no + (tempo_delta * conc)
    return conc_no


def cb_n_amon(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr):
    conc = (coeficientes.k_oa * (1.047 ** (coeficientes.temperatura - 20)) * concentracoes.conc_no
               ) - (f_nitr * concentracoes.conc_n_amon *coeficientes.k_an * (1.08 ** (coeficientes.temperatura - 20))
                   ) + (coeficientes.s_amon * (1.074 ** (coeficientes.temperatura - 20)) / hidraulica.profundidade)
    conc_n_amon = concentracoes.conc_n_amon + (tempo_delta * conc)
    return conc_n_amon


def cb_nitrito(tempo_delta, coeficientes, concentracoes, f_nitr):
    conc = (f_nitr * concentracoes.conc_n_amon * coeficientes.k_an * (1.08 ** (coeficientes.temperatura - 20))
            ) - (f_nitr * concentracoes.conc_nitrito * coeficientes.k_nn * (1.047 ** (coeficientes.temperatura - 20)))
    conc_nitrito = concentracoes.conc_nitrito + (tempo_delta * conc)
    return conc_nitrito


def cb_nitrato(tempo_delta, coeficientes, concentracoes, f_nitr):
    conc = (f_nitr * coeficientes.k_nn * concentracoes.conc_nitrito * (1.047 ** (coeficientes.temperatura - 20)))
    conc_nitrato = concentracoes.conc_nitrato + (tempo_delta * conc)
    return conc_nitrato


def cb_p_org(tempo_delta, coeficientes, concentracoes):
    conc = - ((coeficientes.k_oi * (1.047 ** (coeficientes.temperatura - 20))
               ) + (coeficientes.k_spo * (1.024 ** (coeficientes.temperatura - 20)))) * concentracoes.conc_p_org 
    conc_p_org = concentracoes.conc_p_org + (tempo_delta * conc)
    return conc_p_org


def cb_p_inorg(tempo_delta, coeficientes, concentracoes, hidraulica):
    conc = (coeficientes.k_oi * (1.047 ** (coeficientes.temperatura - 20)) * concentracoes.conc_p_org
            ) + (coeficientes.s_pinorg * (1.074 ** (coeficientes.temperatura - 20)) / hidraulica.profundidade)
    conc_p_inorg = concentracoes.conc_p_inorg + (tempo_delta * conc)
    return conc_p_inorg


def cb_e_coli(tempo_delta, coeficientes, concentracoes):
    conc = - coeficientes.k_b * concentracoes.conc_e_coli * (1.07 ** (coeficientes.temperatura - 20))
    conc_e_coli = concentracoes.conc_e_coli + (tempo_delta * conc)
    return conc_e_coli


def modelagem_as(lista_final, e_coeficientes, lista_s_pontual, lista_e_pontual,
              lista_e_difusa, discretizacao, lista_modelagem, valor_coef, id_coef):
    coef_od = ['k_1', 'k_2', 'k_d', 'k_s', 'l_rd', 's_d', 'r_o2_amon', 'k_oa', 'k_so', 'k_an', 's_amon', 'k_nn', 'k_nit_od', 'temperatura']
    coef_n = ['k_oa', 'k_so', 'k_an', 's_amon', 'k_nn', 'k_nit_od', 'temperatura']
    coef_p = ['k_oi', 'k_spo', 's_pinorg', 'temperatura']
    coef_cf = ['k_b', 'temperatura']
    anaerobiose = [False] * len(lista_e_pontual[0].vazao)
    vazao = 0
    coeficientes = copy.deepcopy(e_coeficientes)
    setattr(coeficientes, id_coef, valor_coef)

    for i in range(len(lista_final)):
        hidraulica = lista_final[i].hidraulica
              
        if i == 0:
            concentracoes = copy.deepcopy(lista_e_pontual[0].concentracoes)

          
        for k in range(len(lista_e_pontual)):
            ep_concetracoes = lista_e_pontual[k].concentracoes
            if hidraulica.comprimento == lista_e_pontual[k].comprimento:
                vazao += lista_e_pontual[k].vazao
                if (lista_modelagem['m_od']) and (id_coef in coef_od):
                    concentracoes.conc_od = mistura(concentracoes.conc_od, ep_concetracoes.conc_od, vazao, lista_e_pontual[k].vazao)
                if (lista_modelagem['m_od']) and (id_coef in coef_od):
                    concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ep_concetracoes.conc_dbo, vazao, lista_e_pontual[k].vazao)
                if (lista_modelagem['m_n']) and (id_coef in coef_n):
                    concentracoes.conc_no = mistura(concentracoes.conc_no, ep_concetracoes.conc_no, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ep_concetracoes.conc_n_amon, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ep_concetracoes.conc_nitrito, vazao, lista_e_pontual[k].vazao)
                if (lista_modelagem['m_p']) and (id_coef in coef_p):
                    concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ep_concetracoes.conc_p_org, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ep_concetracoes.conc_p_inorg, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                if (lista_modelagem['m_c']) and (id_coef in coef_cf):
                    concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ep_concetracoes.conc_e_coli, vazao, lista_e_pontual[k].vazao)

        if len(lista_e_difusa) > 0 :
            for n in range(len(lista_e_difusa)):
                ed_concetracoes = lista_e_difusa[n].concentracoes
                if lista_e_difusa[n].comprimento_inicial <= hidraulica.comprimento <= lista_e_difusa[n].comprimento_final:

                    vazao_difusa = (lista_e_difusa[n].vazao *  discretizacao
                                    ) / (lista_e_difusa[n].comprimento_final - lista_e_difusa[n].comprimento_inicial)
                    vazao += vazao_difusa

                    if (lista_modelagem['m_od']) and (id_coef in coef_od):
                        concentracoes.conc_od = mistura(concentracoes.conc_od, ed_concetracoes.conc_od, hidraulica.vazao, vazao_difusa)
                    if (lista_modelagem['m_od']) and (id_coef in coef_od):
                        concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ed_concetracoes.conc_dbo, hidraulica.vazao, vazao_difusa)
                    if (lista_modelagem['m_n']) and (id_coef in coef_n):
                        concentracoes.conc_no = mistura(concentracoes.conc_no, ed_concetracoes.conc_no, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ed_concetracoes.conc_n_amon, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ed_concetracoes.conc_nitrito, hidraulica.vazao, vazao_difusa)
                    if (lista_modelagem['m_p']) and (id_coef in coef_p):
                        concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ed_concetracoes.conc_p_org, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ed_concetracoes.conc_p_inorg, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                    if (lista_modelagem['m_c']) and (id_coef in coef_cf):
                        concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ed_concetracoes.conc_e_coli, hidraulica.vazao, vazao_difusa)
            

        if len(lista_s_pontual) > 0 :
            for p in range(len(lista_s_pontual)):
                    if hidraulica.comprimento == lista_s_pontual[p].comprimento:
                        vazao -= lista_s_pontual[p].vazao

        tempo_delta = discretizacao / (hidraulica.velocidade * 86400)
            
        if lista_modelagem['m_n']:
            f_nitr = 1 - np.exp(1) ** (- coeficientes.k_nit_od * concentracoes.conc_od)
        else:
            f_nitr = 0 * concentracoes.conc_od
        
        if (lista_modelagem['m_od']) and (id_coef in coef_od):
            concentracoes.conc_od, od_saturacao, anaerobiose = cb_od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, anaerobiose, lista_modelagem['m_n'])
            concentracoes.conc_dbo, anaerobiose = cb_dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose, od_saturacao)
        if (lista_modelagem['m_n']) and (id_coef in coef_n):
            concentracoes.conc_no = cb_no(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_n_amon = cb_n_amon(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr)
            concentracoes.conc_nitrito = cb_nitrito(tempo_delta, coeficientes, concentracoes, f_nitr)
            concentracoes.conc_nitrato = cb_nitrato(tempo_delta, coeficientes, concentracoes, f_nitr)
        if (lista_modelagem['m_p']) and (id_coef in coef_p):
            concentracoes.conc_p_org = cb_p_org(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_p_inorg = cb_p_inorg(tempo_delta, coeficientes, concentracoes, hidraulica)
            concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
        if (lista_modelagem['m_c']) and (id_coef in coef_cf):
            concentracoes.conc_e_coli = cb_e_coli(tempo_delta, coeficientes, concentracoes)
 
    return concentracoes


def ajust_porc(coef_mm, porcentagem):
    media = np.mean([coef_mm[0], coef_mm[1]])
    value_porc = media * (porcentagem / 100)
    min_value = media - value_porc
    max_value = media + value_porc

    return [min_value, max_value], media



def modelagem_as_final(id_chave, lista_hidr_model, lista_media_coef,
                       lista_rio, lista_modelagem, ordem_modelagem,
                       ordem_desague, ponto_af, i_coef, conj_coeficientes):
    if i_coef == None:
        valor_coef = lista_media_coef.temperatura
    else:
        coef = getattr(conj_coeficientes, id_chave)
        valor_coef = coef[i_coef]

    lista_rio_temporaria = copy.deepcopy(lista_rio)
    
    for ior in ordem_modelagem:
        dados = lista_rio_temporaria[ior]
        conc_final = modelagem_as(lista_hidr_model[ior], lista_media_coef, dados.lista_s_pontual,
                                  dados.lista_e_pontual, dados.lista_e_difusa,
                                  dados.discretizacao, lista_modelagem, valor_coef, id_chave)
        
        if ior != 0:
            comp = menor_dist2(lista_rio_temporaria[ordem_desague[ior - 1]], ponto_af[ior - 1][1],
                               ponto_af[ior - 1][2], ponto_af[ior - 1][3])

            afluente = EntradaPontual(ponto_af[ior - 1][1], ponto_af[ior - 1][2],
                                      comp, conc_final, lista_hidr_model[ior][-1].hidraulica.vazao,
                                      ponto_af[ior - 1][0], ior)
            
            lista_rio_temporaria[ordem_desague[ior - 1]].lista_e_pontual.append(copy.deepcopy(afluente))
        
    return conc_final, id_chave


def modelagem_calib(e_coeficientes, lista_final, lista_s_pontual, lista_e_pontual,
              lista_e_difusa, discretizacao, lista_modelagem, ordem_dr, dados_reais_to):

    anaerobiose = [False] * len(lista_e_pontual[0].vazao)
    vazao = 0
    coeficientes = copy.deepcopy(e_coeficientes)
    lista_concentracoes = []

    for i in range(len(lista_final)):
        hidraulica = lista_final[i].hidraulica
               
        if i == 0:
            concentracoes = copy.deepcopy(lista_e_pontual[0].concentracoes)
                       
          
        for k in range(len(lista_e_pontual)):
            ep_concetracoes = lista_e_pontual[k].concentracoes
            if hidraulica.comprimento == lista_e_pontual[k].comprimento:
                vazao += lista_e_pontual[k].vazao
                if lista_modelagem['m_od']:
                    concentracoes.conc_od = mistura(concentracoes.conc_od, ep_concetracoes.conc_od, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_od']:
                    concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ep_concetracoes.conc_dbo, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_n']:
                    concentracoes.conc_no = mistura(concentracoes.conc_no, ep_concetracoes.conc_no, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ep_concetracoes.conc_n_amon, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ep_concetracoes.conc_nitrito, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_p']:
                    concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ep_concetracoes.conc_p_org, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ep_concetracoes.conc_p_inorg, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                if lista_modelagem['m_c']:
                    concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ep_concetracoes.conc_e_coli, vazao, lista_e_pontual[k].vazao)

        if len(lista_e_difusa) > 0 :
            for n in range(len(lista_e_difusa)):
                ed_concetracoes = lista_e_difusa[n].concentracoes
                if lista_e_difusa[n].comprimento_inicial <= hidraulica.comprimento <= lista_e_difusa[n].comprimento_final:

                    vazao_difusa = (lista_e_difusa[n].vazao *  discretizacao
                                    ) / (lista_e_difusa[n].comprimento_final - lista_e_difusa[n].comprimento_inicial)
                    vazao += vazao_difusa

                    if lista_modelagem['m_od']:
                        concentracoes.conc_od = mistura(concentracoes.conc_od, ed_concetracoes.conc_od, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_od']:
                        concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ed_concetracoes.conc_dbo, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_n']:
                        concentracoes.conc_no = mistura(concentracoes.conc_no, ed_concetracoes.conc_no, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ed_concetracoes.conc_n_amon, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ed_concetracoes.conc_nitrito, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_p']:
                        concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ed_concetracoes.conc_p_org, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ed_concetracoes.conc_p_inorg, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                    if lista_modelagem['m_c']:
                        concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ed_concetracoes.conc_e_coli, hidraulica.vazao, vazao_difusa)
    
        if len(lista_s_pontual) > 0 :
            for p in range(len(lista_s_pontual)):
                    if hidraulica.comprimento == lista_s_pontual[p].comprimento:
                        vazao -= lista_s_pontual[p].vazao

        tempo_delta = discretizacao / (hidraulica.velocidade * 86400)
        if lista_modelagem['m_n']:
            f_nitr = 1 - np.exp(1) ** (- coeficientes.k_nit_od * concentracoes.conc_od)
        else:
            f_nitr = 0 * concentracoes.conc_od
            
        
        
        if lista_modelagem['m_od']:
            concentracoes.conc_od, od_saturacao, anaerobiose = cb_od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, anaerobiose, lista_modelagem['m_n'])
            concentracoes.conc_dbo, anaerobiose = cb_dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose, od_saturacao)
        if lista_modelagem['m_n']:
            concentracoes.conc_no = cb_no(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_n_amon = cb_n_amon(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr)
            concentracoes.conc_nitrito = cb_nitrito(tempo_delta, coeficientes, concentracoes, f_nitr)
            concentracoes.conc_nitrato = cb_nitrato(tempo_delta, coeficientes, concentracoes, f_nitr)
        if lista_modelagem['m_p']:
            concentracoes.conc_p_org = cb_p_org(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_p_inorg = cb_p_inorg(tempo_delta, coeficientes, concentracoes, hidraulica)
            concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
        if lista_modelagem['m_c']:
            concentracoes.conc_e_coli = cb_e_coli(tempo_delta, coeficientes, concentracoes)

        if ordem_dr == None:
            if i == (len(lista_final) - 1):
                lista_concentracoes.append(copy.deepcopy(concentracoes))
                
        else:
            for dr_to in range(len(dados_reais_to)):
                if hidraulica.comprimento == dados_reais_to[dr_to].comprimento:
                    lista_concentracoes.append(copy.deepcopy(concentracoes))
                    

    return lista_concentracoes


def modelagem_calib_final(lista_pos, seq_coef, lista_hidr_model,
                          list_tranfor, lista_modelagem, ordem_rio,
                          ordem_desague, ponto_af, fixar_coef,
                          ordem_dr, trecho_hidr):
    e_coeficientes = copy.deepcopy(fixar_coef)
    for id_c in range(len(seq_coef)):
        setattr(e_coeficientes, seq_coef[id_c], lista_pos[id_c])
    
    lista_rio_temporaria = copy.deepcopy(list_tranfor)
    
    for ior in ordem_rio:
        dados = lista_rio_temporaria[ior]

        if ior == ordem_rio[-1]:
            lista_conc_final = modelagem_calib(e_coeficientes, trecho_hidr, dados.lista_s_pontual,
                                    dados.lista_e_pontual, dados.lista_e_difusa,
                                    dados.discretizacao, lista_modelagem, ordem_dr, dados.lista_dados_reais)
        
        else:
            lista_conc_final = modelagem_calib(e_coeficientes, lista_hidr_model[ior], dados.lista_s_pontual,
                                    dados.lista_e_pontual, dados.lista_e_difusa,
                                    dados.discretizacao, lista_modelagem, None, None)
            
            comp = menor_dist2(lista_rio_temporaria[ordem_desague[ior - 1]], ponto_af[ior - 1][1],
                               ponto_af[ior - 1][2], ponto_af[ior - 1][3])

            afluente = EntradaPontual(ponto_af[ior - 1][1], ponto_af[ior - 1][2],
                                      comp, lista_conc_final[0], lista_hidr_model[ior][-1].hidraulica.vazao,
                                      ponto_af[ior - 1][0], ior)
            
            lista_rio_temporaria[ordem_desague[ior - 1]].lista_e_pontual.append(copy.deepcopy(afluente))
        

        
    return lista_conc_final


def modelagem_2(lista_final, lista_e_coeficientes, lista_s_pontual, lista_e_pontual,
              lista_e_difusa, rio, discretizacao, lista_modelagem):
    anaerobiose = [False] * len(lista_e_pontual[0].vazao)
    vazao = 0
    coeficientes = Coeficientes(None, None, None, None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None, None, None, None)

    for i in range(len(lista_final)):
        hidraulica = lista_final[i].hidraulica
        
        for j in range(len(lista_e_coeficientes)):
            atual = lista_e_coeficientes[j]
            if atual.comprimento == hidraulica.comprimento:
                k_2_calculavel = atual.coeficientes.k_2_calculavel
                k_2_max = atual.coeficientes.k_2_max
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
            concentracoes = copy.deepcopy(lista_e_pontual[0].concentracoes)

          
        for k in range(len(lista_e_pontual)):
            ep_concetracoes = lista_e_pontual[k].concentracoes
            if hidraulica.comprimento == lista_e_pontual[k].comprimento:
                vazao += lista_e_pontual[k].vazao
                if lista_modelagem['m_od']:
                    concentracoes.conc_od = mistura(concentracoes.conc_od, ep_concetracoes.conc_od, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_od']:
                    concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ep_concetracoes.conc_dbo, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_n']:
                    concentracoes.conc_no = mistura(concentracoes.conc_no, ep_concetracoes.conc_no, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ep_concetracoes.conc_n_amon, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ep_concetracoes.conc_nitrito, vazao, lista_e_pontual[k].vazao)
                if lista_modelagem['m_p']:
                    concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ep_concetracoes.conc_p_org, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ep_concetracoes.conc_p_inorg, vazao, lista_e_pontual[k].vazao)
                    concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                if lista_modelagem['m_c']:
                    concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ep_concetracoes.conc_e_coli, vazao, lista_e_pontual[k].vazao)

        if len(lista_e_difusa) > 0 :
            for n in range(len(lista_e_difusa)):
                ed_concetracoes = lista_e_difusa[n].concentracoes
                if lista_e_difusa[n].comprimento_inicial <= hidraulica.comprimento <= lista_e_difusa[n].comprimento_final:

                    vazao_difusa = (lista_e_difusa[n].vazao *  discretizacao
                                    ) / (lista_e_difusa[n].comprimento_final - lista_e_difusa[n].comprimento_inicial)
                    vazao += vazao_difusa

                    if lista_modelagem['m_od']:
                        concentracoes.conc_od = mistura(concentracoes.conc_od, ed_concetracoes.conc_od, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_od']:
                        concentracoes.conc_dbo = mistura(concentracoes.conc_dbo, ed_concetracoes.conc_dbo, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_n']:
                        concentracoes.conc_no = mistura(concentracoes.conc_no, ed_concetracoes.conc_no, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_n_amon = mistura(concentracoes.conc_n_amon, ed_concetracoes.conc_n_amon, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_nitrito = mistura(concentracoes.conc_nitrito, ed_concetracoes.conc_nitrito, hidraulica.vazao, vazao_difusa)
                    if lista_modelagem['m_p']:
                        concentracoes.conc_p_org = mistura(concentracoes.conc_p_org, ed_concetracoes.conc_p_org, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_inorg = mistura(concentracoes.conc_p_inorg, ed_concetracoes.conc_p_inorg, hidraulica.vazao, vazao_difusa)
                        concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
                    if lista_modelagem['m_c']:
                        concentracoes.conc_e_coli = mistura(concentracoes.conc_e_coli, ed_concetracoes.conc_e_coli, hidraulica.vazao, vazao_difusa)
    
        if len(lista_s_pontual) > 0 :
            for p in range(len(lista_s_pontual)):
                    if hidraulica.comprimento == lista_s_pontual[p].comprimento:
                        vazao -= lista_s_pontual[p].vazao


        tempo_delta = discretizacao / (hidraulica.velocidade * 86400)
        
        if lista_modelagem['m_n']:
            f_nitr = 1 - np.exp(1) ** (- coeficientes.k_nit_od * concentracoes.conc_od)
        else:
            f_nitr = 0 * concentracoes.conc_od
        
        if lista_modelagem['m_od']:
            concentracoes.conc_od, od_saturacao, anaerobiose = cb_od(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr, anaerobiose, lista_modelagem['m_n'])
            concentracoes.conc_dbo, anaerobiose = cb_dbo(tempo_delta, coeficientes, concentracoes, hidraulica, anaerobiose, od_saturacao)
        if lista_modelagem['m_n']:
            concentracoes.conc_no = cb_no(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_n_amon = cb_n_amon(tempo_delta, coeficientes, concentracoes, hidraulica, f_nitr)
            concentracoes.conc_nitrito = cb_nitrito(tempo_delta, coeficientes, concentracoes, f_nitr)
            concentracoes.conc_nitrato = cb_nitrato(tempo_delta, coeficientes, concentracoes, f_nitr)
        if lista_modelagem['m_p']:
            concentracoes.conc_p_org = cb_p_org(tempo_delta, coeficientes, concentracoes)
            concentracoes.conc_p_inorg = cb_p_inorg(tempo_delta, coeficientes, concentracoes, hidraulica)
            concentracoes.conc_p_total = concentracoes.conc_p_org + concentracoes.conc_p_inorg
        if lista_modelagem['m_c']:
            concentracoes.conc_e_coli = cb_e_coli(tempo_delta, coeficientes, concentracoes)
 
        lista_final[i].concentracoes = copy.deepcopy(concentracoes)
        lista_final[i].coeficientes = copy.deepcopy(coeficientes)
        lista_final[i].rio = rio
    return lista_final


def modelagem_Final_2(lista_rio, ponto_af, lista_modelagem,
                    ordem_desague, ordem_modelagem, lista_hidr_model):
    
    lista_completa_final = []
    marc = 0
    for ior in ordem_modelagem:
        dados = lista_rio[ior]
        lista_final = modelagem_2(lista_hidr_model[marc], dados.lista_e_coeficientes, dados.lista_s_pontual,
                                dados.lista_e_pontual, dados.lista_e_difusa, dados.rio,
                                dados.discretizacao, lista_modelagem)
        marc += 1
        if ior != 0:
            comp = menor_dist2(lista_rio[ordem_desague[ior - 1]], ponto_af[ior - 1][1],
                               ponto_af[ior - 1][2], ponto_af[ior - 1][3])

            afluente = EntradaPontual(ponto_af[ior - 1][1], ponto_af[ior - 1][2],
                                      comp, lista_final[-1].concentracoes,
                                      lista_final[-1].hidraulica.vazao, ponto_af[ior - 1][0], lista_final[-1].rio)
            
            lista_rio[ordem_desague[ior - 1]].lista_e_pontual.append(copy.deepcopy(afluente))
        
        lista_completa_final.append(copy.deepcopy(lista_final))
    return lista_completa_final, lista_rio[0].lista_e_pontual


def salvando_conc(list_tranfor, ordem_final, marcador_conj_global,
                  trecho_hidr, coef_ponto, lista_modelagem, lista_hidr_model, ordem_desague, ponto_af):
    ordem_rio = ordem_final[marcador_conj_global]
    for ior in ordem_rio:
        dados = list_tranfor[ior]

        if ior == ordem_rio[-1]:
            lista_conc_final = modelagem_calib(coef_ponto, trecho_hidr, dados.lista_s_pontual,
                                    dados.lista_e_pontual, dados.lista_e_difusa,
                                    dados.discretizacao, lista_modelagem, None, None)
            comp = trecho_hidr[-1].hidraulica.comprimento
            afluente = EntradaPontual(None, None, comp, copy.deepcopy(lista_conc_final[0]), trecho_hidr[-1].hidraulica.vazao,
                                      None, ior)
            list_tranfor[0].lista_e_pontual.append(copy.deepcopy(afluente))

        
        else:
            lista_conc_final = modelagem_calib(coef_ponto, lista_hidr_model[ior], dados.lista_s_pontual,
                                    dados.lista_e_pontual, dados.lista_e_difusa,
                                    dados.discretizacao, lista_modelagem, None, None)
            
            comp = menor_dist2(list_tranfor[ordem_desague[ior - 1]], ponto_af[ior - 1][1],
                               ponto_af[ior - 1][2], ponto_af[ior - 1][3])

            afluente = EntradaPontual(ponto_af[ior - 1][1], ponto_af[ior - 1][2],
                                      comp, lista_conc_final[0], lista_hidr_model[ior][-1].hidraulica.vazao,
                                      ponto_af[ior - 1][0], ior)
            
            list_tranfor[ordem_desague[ior - 1]].lista_e_pontual.append(copy.deepcopy(afluente))
    return list_tranfor