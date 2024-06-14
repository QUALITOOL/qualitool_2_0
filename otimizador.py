import numpy as np
import random
import copy
from equacoes import equacoes_calibragem

# Parametros iniciais para AG
limite_geracao = 100
tam_pop = 100
n_ger = 100
pm = 0.5  # taxa de mutação
pc = 0.8  # taxa de crossover
n_elitismo = 2
random.seed()

# Coeficientes calibravéis
comp_max = 1000
comp_min = 1
coef_max = [comp_max]
coef_min = [comp_min]


# Aptidão
def calcula_aptidao(conjunto, cr_seq):
    k2 = cr_seq[0]
    lista_parametros = conjunto[0]
    lista_coeficientes = conjunto[1]
    lista_despejos = conjunto[2]
    lista_retirada = conjunto[3]
    delta = conjunto[4]
    index = conjunto[5]

    list_parametros_finais, list_final = equacoes_calibragem(
        lista_parametros, lista_coeficientes, lista_despejos,
        lista_retirada, delta, index, k2)

    soma_1 = []
    lista_delta = list_final[0]
    list_od_final = list_final[2]
    dist_real = [0, 5, 7, 13, 22, 31, 40, 50, 100]
    od_real = [6.9, 5.4, 4.7, 4, 3.5, 4.1, 3.6, 2, 3.5]
    od_calc = []
    for i in range(len(lista_delta)):
        if lista_delta[i] in dist_real:
            index_1 = dist_real.index(lista_delta[i])
            od_calc.append(list_od_final[index_1])
    # F1
    for i in range(len(dist_real)):
        soma_1.append((od_calc[i] - od_real[i])**2)

    return np.mean(soma_1)


# Cromossomos - orinetanção de objeto
class Cromossomo:
    def __init__(self, cr_seq, aptidao):
        self.cr_seq = cr_seq
        self.aptidao = aptidao


# Gerando a população
def gera_populacao_inicial(tam_pop, conjunto):
    lista_populacao = []
    for _ in range(tam_pop):
        lista_cr = []
        for i in range(len(coef_max)):
            lista_cr.append(random.uniform(coef_min[i], coef_max[i]))
        aptidao = calcula_aptidao(conjunto, lista_cr)
        cromossomo = Cromossomo(lista_cr, aptidao)
        lista_populacao.append(cromossomo)
    return lista_populacao


# Elitismo
def elitismo(populacao):
    i_melhores = []
    cr_elites = []
    for _ in range(n_elitismo):
        melhor_aptidao = 999999999
        indice_melhor = -1
        for i in range(len(populacao)):
            if populacao[i].aptidao < melhor_aptidao and not (i in i_melhores):
                melhor_aptidao = populacao[i].aptidao
                indice_melhor = i
        i_melhores.append(indice_melhor)
        cr_elites.append(copy.deepcopy(populacao[indice_melhor]))
    return cr_elites


# Evolução diferencial
def evolucao_diferencial(populacao, conjunto):
    lista_ed = elitismo(populacao)
    for cr in range(int(tam_pop - n_elitismo)):
        cr_atual = populacao[cr]
        cr_xs = random.sample(populacao, 3)
        while cr_xs[0] == cr_xs[1] or cr_xs[
            0] == cr_xs[2] or cr_xs[1] == cr_xs[2] or cr_atual == cr_xs[
                0] or cr_atual == cr_xs[1] or cr_atual == cr_xs[2]:
            cr_xs = random.sample(populacao, 3)
        cr_1 = cr_xs[0].cr_seq
        cr_2 = cr_xs[1].cr_seq
        cr_3 = cr_xs[2].cr_seq
        pre_trial = []
        trial = []
        for i in range(len(cr_atual.cr_seq)):
            valor = cr_1[i] + pm * (cr_3[i] - cr_2[i])
            if valor < coef_min[i]:
                valor = coef_min[i]
            elif valor > coef_max[i]:
                valor = coef_max[i]
            pre_trial.append(valor)

        for j in range(len(cr_atual.cr_seq)):
            sort_pc = random.uniform(0.0, 1.0)
            if sort_pc < pc:
                trial.append(pre_trial[j])
            else:
                trial.append(cr_atual.cr_seq[j])
        aptidao_trial = calcula_aptidao(conjunto, trial)
        if aptidao_trial < cr_atual.aptidao:
            cr_atual.cr_seq = trial
            cr_atual.aptidao = aptidao_trial
        lista_ed.append(copy.deepcopy(cr_atual))
    return lista_ed


# Imprimindo melhores resultados
def melhores_resultados(populacao):
    melhor_cr = populacao[0]
    for cr in populacao:
        if cr.aptidao < melhor_cr.aptidao:
            melhor_cr = cr
    return melhor_cr


# Main
def algoritimo(conjunto):
    n_variavel = 0
    n_rep = 0
    for _ in range(1):
        pop = gera_populacao_inicial(tam_pop, conjunto)
        lista_melhor_aptidao = []
        lista_melhor_seq = []
        cr = melhores_resultados(pop)
        lista_melhor_aptidao.append(cr.aptidao)
        lista_melhor_seq.append(cr.cr_seq)
        aptidao_ant = cr.aptidao

        while n_variavel < n_ger and n_rep < 10:
            pop = evolucao_diferencial(pop, conjunto)
            cr = melhores_resultados(pop)
            lista_melhor_aptidao.append(cr.aptidao)
            lista_melhor_seq.append(cr.cr_seq)
            n_variavel += 1
            if cr.aptidao == aptidao_ant:
                n_rep += 1
            else:
                n_rep = 0
            aptidao_ant = cr.aptidao
        melhor_comp = lista_melhor_seq[-1]
        melhor_aptidao = lista_melhor_aptidao[-1]
    return melhor_comp[0], melhor_aptidao, n_variavel
