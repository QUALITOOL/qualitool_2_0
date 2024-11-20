import streamlit as st
import pandas as pd
import numpy as np
import copy


def dados_reais(data, n_tributarios, labels, lista_tabs, list_name, list_valores, lista_modelagem, dias):

    list_col_dados = ['ID (opcional)',
                      'Latitude (UTM)',
                      'Longitude (UTM)',
                      'Comprimento (m)',
                      'Q (m³/s)']
    list_name.pop(0)
    list_valores.pop(0)
    if lista_modelagem['s_t']:
        list_name.pop(0)
        list_valores.pop(0)

    expander = st.expander(
        "**:green[DADOS OBSERVADOS]**")
     
    col4_1, col4_2 = expander.columns(2)
    col4_2.warning('''Adicionar ou a **Latitude e Longitude** ou o **Comprimento**.''',
                    icon="❕")
    

    if lista_modelagem['s_t']:
        list_name_dr = ['Data'] + list_col_dados + list_name
        list_valores_dr = [[None], [0.0], [None], [None], [None], [0.0]] + list_valores
    else:
        list_name_dr = list_col_dados + list_name
        list_valores_dr = [[0.0], [None], [None], [None], [0.0]] + list_valores
    
    
    df_dr2 = pd.DataFrame(columns=list_name_dr)

    if data != False:
        list_valores_dr = data['Contr e Retir']['l_dr'][1]

    for yc in range(len(list_name_dr)):
        df_dr2[list_name_dr[yc]] = list_valores_dr[yc]

    df_dr2_f = expander.data_editor(df_dr2, 
                                        column_config={
                                            'Data':st.column_config.DateColumn(
                                                format="MM.DD.YYYY", step=1),
                                                },
                                            disabled=[None])
    list_valores_dr = []
    for epf in range(len(list_name_dr)):
        if epf == 0 and lista_modelagem['s_t'] == True:
            pass
        else:
            list_valores_dr.append(list(df_dr2_f[list_name_dr[epf]]))    

    


    return


def coef_intervalo():
    expander = st.expander(
        "**:green[INTEVALO DE BUSCA DOS COEFICIENTES]**")
        
    expander.text('f')


    return


def parametros_pso():
    expander = st.expander(
        "**:green[PARÂMETROS DO PSO - OPCIONAL]**")
    
    col1, col2 = expander.columns(2)    
    col2_1, col2_2 = col2.columns(2)
    tam_enxame = col2_1.number_input("❗ Tamanho do enxame:", value=15, min_value=1)
    n_ger = col2_2.number_input("❗ Número de interações", value=30, min_value=1)
    col2.warning('''Atenção! Em caso de atualização da tela, os dados 
                já preenchidos serão perdidos e precisarão ser 
                inseridos novamente.''',
                  icon="⚠️")
    w = col1.slider("Inércia:", 0.0, 2.0, 0.9)
    c1 = col1.slider("Componente cognitiva (pessoal):", 0.0, 2.0, 1.8)
    c2 = col1.slider("Componente social (global):", 0.0, 2.0, 2.0)

    return