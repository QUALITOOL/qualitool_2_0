from concurrent.futures import ThreadPoolExecutor
from functools import partial
import numpy as np
import random
import copy
from funcoes.equacoes import modelagem_calib_final
import streamlit as st

# Particula
class Particula:
    def __init__(self, posicao, aptidao, velocidade, melhor_pos_ind, melhor_apt_ind):
        self.posicao = posicao
        self.aptidao = aptidao
        self.velocidade = velocidade
        self.melhor_pos_ind = melhor_pos_ind
        self.melhor_apt_ind = melhor_apt_ind


# Aptidão
def calc_aptidao(seq_coef, lista_lista_pos, list_tranfor, fixar_coef,
                 ordem_dr, ponto_af, lista_modelagem, lista_hidr_model,
                 ordem_desague, ordem_rio, trecho_hidr, dias):
    
    
    precisao = 5
    lista_aptidoes = []
    partial_function = partial(modelagem_calib_final,
                            seq_coef=seq_coef,
                            lista_hidr_model=lista_hidr_model,
                            list_tranfor=list_tranfor,
                            lista_modelagem=lista_modelagem,
                            ordem_rio=ordem_rio,
                            ordem_desague=ordem_desague,
                            ponto_af=ponto_af,
                            fixar_coef=fixar_coef,
                            ordem_dr=ordem_dr,
                            trecho_hidr=trecho_hidr)


    with ThreadPoolExecutor() as executor:
        
        resultados = list(executor.map(partial_function, lista_lista_pos))

    for lista_conc_final in resultados:
        list_sim_real = {}
        if lista_modelagem['m_od']:
            list_sim_real['conc_od'] = {'real':[], 'simulado': []}
            list_sim_real['conc_dbo'] = {'real':[], 'simulado': []}
        if lista_modelagem['m_n']:
            list_sim_real['conc_no'] = {'real':[], 'simulado': []}
            list_sim_real['conc_n_amon'] = {'real':[], 'simulado': []}
            list_sim_real['conc_nitrito'] = {'real':[], 'simulado': []}
        if lista_modelagem['m_p']:
            list_sim_real['conc_p_org'] = {'real':[], 'simulado': []}
            list_sim_real['conc_p_inorg'] = {'real':[], 'simulado': []}
        if lista_modelagem['m_c']:
            list_sim_real['conc_e_coli'] = {'real':[], 'simulado': []}

        nome_modelos = list(list_sim_real.keys())

        
        if lista_modelagem['s_t']:
            for id_dias in range(len(dias)):
                for id_dr in range(len(ordem_dr)):
                    lista_dador = list_tranfor[ordem_rio[-1]].lista_dados_reais[ordem_dr[id_dr]]
                    for id_dia_dr in range(len(lista_dador.data_dr)):

                        if dias[id_dias].date() == lista_dador.data_dr[id_dia_dr].date():
                            if lista_modelagem['m_od']:
                                list_sim_real['conc_od']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_od[id_dia_dr]))
                                list_sim_real['conc_od']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_od[id_dias]))
                                list_sim_real['conc_dbo']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_dbo[id_dia_dr]))
                                list_sim_real['conc_dbo']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_dbo[id_dias]))
                            if lista_modelagem['m_n']:
                                list_sim_real['conc_no']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_no[id_dia_dr]))
                                list_sim_real['conc_no']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_no[id_dias]))
                                list_sim_real['conc_n_amon']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_n_amon[id_dia_dr]))
                                list_sim_real['conc_n_amon']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_n_amon[id_dias]))
                                list_sim_real['conc_nitrito']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_nitrito[id_dia_dr]))
                                list_sim_real['conc_nitrito']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_nitrito[id_dias]))
                            if lista_modelagem['m_p']:
                                list_sim_real['conc_p_org']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_org[id_dia_dr]))
                                list_sim_real['conc_p_org']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_org[id_dias]))
                                list_sim_real['conc_p_inorg']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_inorg[id_dia_dr]))
                                list_sim_real['conc_p_inorg']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_inorg[id_dias]))
                            if lista_modelagem['m_c']:
                                list_sim_real['conc_e_coli']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_e_coli[id_dia_dr]))
                                list_sim_real['conc_e_coli']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_e_coli[id_dias]))
        else:
            
            for id_dr in range(len(ordem_dr)):
                lista_dador = list_tranfor[ordem_rio[-1]].lista_dados_reais[ordem_dr[id_dr]]
                if lista_modelagem['m_od']:
                    list_sim_real['conc_od']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_od[0]))
                    list_sim_real['conc_od']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_od[0]))
                    list_sim_real['conc_dbo']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_dbo[0]))
                    list_sim_real['conc_dbo']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_dbo[0]))
                if lista_modelagem['m_n']:
                    list_sim_real['conc_no']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_no[0]))
                    list_sim_real['conc_no']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_no[0]))
                    list_sim_real['conc_n_amon']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_n_amon[0]))
                    list_sim_real['conc_n_amon']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_n_amon[0]))
                    list_sim_real['conc_nitrito']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_nitrito[0]))
                    list_sim_real['conc_nitrito']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_nitrito[0]))
                if lista_modelagem['m_p']:
                    list_sim_real['conc_p_org']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_org[0]))
                    list_sim_real['conc_p_org']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_org[0]))
                    list_sim_real['conc_p_inorg']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_p_inorg[0]))
                    list_sim_real['conc_p_inorg']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_p_inorg[0]))
                if lista_modelagem['m_c']:
                    list_sim_real['conc_e_coli']['real'].append(copy.deepcopy(lista_dador.concentracoes.conc_e_coli[0]))
                    list_sim_real['conc_e_coli']['simulado'].append(copy.deepcopy(lista_conc_final[id_dr].conc_e_coli[0]))

          
        lista_coef_Nash_Sutcliffe = []
        for model in nome_modelos:
            soma_1 = 0
            soma_2 = 0
            if len(list_sim_real[model]['simulado']) > 0:
                for id in range(len(list_sim_real[model]['simulado'])):
                    soma_1 += (list_sim_real[model]['real'][id] - list_sim_real[model]['simulado'][id])**2
                    soma_2 += (list_sim_real[model]['real'][id] - np.mean(list_sim_real[model]['real']))**2

                if len(list_sim_real[model]['simulado']) == 1 or soma_2 == 0:
                    f_1 = 1 - (soma_1 / 0.0001)
                else:
                    f_1 = 1 - (soma_1 / soma_2)


                lista_coef_Nash_Sutcliffe.append(abs(1 - f_1))
                
            else:
                lista_coef_Nash_Sutcliffe = [9999]

        lista_coef_Nash_Sutcliffe = np.array(lista_coef_Nash_Sutcliffe)

        media_desvios = np.mean(lista_coef_Nash_Sutcliffe)
        
        pior_desvio = np.max(lista_coef_Nash_Sutcliffe)
        
        # Soft-Minimax: Média + Penalização proporcional ao pior caso
        
        aptidao_equilibrada = media_desvios + 0.5 * pior_desvio

        lista_aptidoes.append(round(aptidao_equilibrada, precisao))

    return lista_aptidoes

# Gerando enxame
def gera_enxame_inicial(tam_pop, seq_coef, coef_max_min, list_tranfor, fixar_coef,
                        ordem_dr, ponto_af, lista_modelagem, lista_hidr_model,
                        ordem_desague, ordem_rio, trecho_hidr, dias):
    
    lista_enxame = []
    lista_lista_pos = []

    for p in range(tam_pop):
        lista_pos = []
        lista_vel = []

        for nome_coef in seq_coef:
            var = getattr(coef_max_min, nome_coef)
            min_val, max_val = var[0], var[1]
            amplitude = max_val - min_val
            
            # Posição aleatória dentro dos limites reais
            pos = random.uniform(min_val, max_val)
            lista_pos.append(pos)
            
            # Velocidade proporcional à amplitude da variável (ex: 10% da amplitude)
            vel = random.uniform(-0.1 * amplitude, 0.1 * amplitude)
            lista_vel.append(vel)
            
        lista_lista_pos.append(lista_pos)

        # Cria a partícula
        particula = Particula(
            copy.deepcopy(lista_pos), 
            None, # aptidao inicial
            copy.deepcopy(lista_vel), 
            copy.deepcopy(lista_pos), # melhor_pos_ind
            None  # melhor_apt_ind
        )
        lista_enxame.append(particula)

    # Cálculo da aptidão de todo o enxame
    list_aptidao = calc_aptidao(seq_coef, lista_lista_pos, list_tranfor, fixar_coef,
                                ordem_dr, ponto_af, lista_modelagem, lista_hidr_model,
                                ordem_desague, ordem_rio, trecho_hidr, dias)
    
    # Define os melhores globais e individuais
    melhor_aptidao_geral = float('inf') # Se for minimização
    melhor_posicao_geral = None

    for p in range(tam_pop):
        aptidao = list_aptidao[p]
        lista_enxame[p].aptidao = aptidao
        lista_enxame[p].melhor_apt_ind = aptidao
        
        # Atualiza a melhor posição geral com a partícula CORRETA
        if aptidao < melhor_aptidao_geral:
            melhor_aptidao_geral = aptidao
            melhor_posicao_geral = copy.deepcopy(lista_enxame[p].posicao)
    
    return lista_enxame, melhor_posicao_geral, melhor_aptidao_geral


# Melhores resultados
def melhores_resultados(populacao):
    soma_aptidao = 0
    melhor_cr = populacao[0]
    for cr in populacao:
        soma_aptidao += cr.aptidao
        if cr.aptidao < melhor_cr.aptidao:
            melhor_cr = cr
    media_aptidao = soma_aptidao / len(populacao)
    return media_aptidao, melhor_cr

def dict_obtj(enxame, ger, list_dict_apt):
    for enx_i in enxame:
        list_dict_apt['apt'].append(enx_i.aptidao)
        list_dict_apt['ger'].append(ger)
    return list_dict_apt

# PSO
def pso(enxame, w, c1, c2, seq_coef, coef_max_min, list_tranfor, fixar_coef,
        ordem_dr, ponto_af, lista_modelagem, lista_hidr_model,
        ordem_desague, ordem_rio, trecho_hidr, dias, melhor_posicao_geral, melhor_aptidao_geral):
    precisao = 5
    # Atualizar o melhor geral antes do passo
    for i in range(len(enxame)):
        if enxame[i].aptidao < melhor_aptidao_geral:
            melhor_posicao_geral = enxame[i].posicao
            melhor_aptidao_geral = enxame[i].aptidao

    count = 0
    list_lista_posicao = []
    list_lista_veloc = []
    
    for j in range(len(enxame)):
        var = enxame[j]
        lista_veloc = []
        lista_posicao = []
        
        for k in range(len(var.posicao)):
            r1, r2 = random.random(), random.random()
            
            # Limites e Amplitude do Coeficiente k
            max_min = getattr(coef_max_min, seq_coef[k])
            min_val, max_val = max_min[0], max_min[1]
            amplitude = max_val - min_val
            
            # Limite Máximo de Velocidade
            v_max = 0.05 * amplitude
            
            # 1. Equação Clássica da Velocidade
            vel = (w * var.velocidade[k]
                ) + (c1 * r1 * (var.melhor_pos_ind[k] - var.posicao[k])
                ) + (c2 * r2 * (melhor_posicao_geral[k] - var.posicao[k]))
            
            # 2. Trava de Velocidade (Impede explosão)
            vel = max(-v_max, min(v_max, vel))
            
            # 3. Posição Tentativa
            pos = round(var.posicao[k] + vel, precisao)
            
            # 4. Fronteira ABSORVENTE (Corrige o travamento nos extremos)
            if pos < min_val:
                pos = min_val
                vel = 0.0  # Zera a velocidade na parede
            elif pos > max_val:
                pos = max_val
                vel = 0.0  # Zera a velocidade na parede
                
            lista_veloc.append(vel)
            lista_posicao.append(pos)
            
        list_lista_posicao.append(lista_posicao)
        list_lista_veloc.append(lista_veloc)
        
    # Recalcula aptidão das novas posições
    lista_aptidao_atual = calc_aptidao(seq_coef, list_lista_posicao, list_tranfor, fixar_coef,
                                    ordem_dr, ponto_af, lista_modelagem, lista_hidr_model,
                                    ordem_desague, ordem_rio, trecho_hidr, dias)
    
    # Atualiza as partículas do enxame
    for j in range(len(enxame)):
        var = enxame[j]
        aptidao_atual = lista_aptidao_atual[j]
        lista_veloc = list_lista_veloc[j]
        lista_posicao = list_lista_posicao[j]
        
        if var.aptidao == melhor_aptidao_geral and count == 0:
            count = 1
            if aptidao_atual > var.aptidao:
                lista_veloc = var.velocidade
                lista_posicao = var.posicao
                aptidao_atual = var.aptidao

        var.velocidade = lista_veloc
        var.posicao = lista_posicao
        if aptidao_atual < var.melhor_apt_ind:
            var.melhor_pos_ind = var.posicao
            var.melhor_apt_ind = aptidao_atual
        var.aptidao = aptidao_atual
    
    lista_pso = copy.deepcopy(enxame)
    return lista_pso, melhor_posicao_geral, melhor_aptidao_geral

