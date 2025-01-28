import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


bar = st.sidebar
bar.warning('''Atenção! As tabelas com os resultados finais podem 
            ser baixadas ao final da modelagem/calibração.''',
            icon="⚠️")
st.markdown('##### :orange[Plotagem dos resultados (Opcional)]')
uploaded_file = st.file_uploader("Submeter o arquivo .csv"
                            + " construído na etapa de modelagem/calibração:",
                            type=["csv"])
if uploaded_file is None:
    st.markdown("""❗ Obs.: Evite alterar o arquivo gerado na modelagem
        utilizando o Excel. Se os dados não preencherem automaticamente,
        recomenda-se excecutar a modelagem novamente.""")
    
else:
    st.markdown('''<h4 style='text-align: center;
            color: teal;
            '>Visualização de dados </h4>''',
            unsafe_allow_html=True)
    df_data = pd.read_csv(uploaded_file, index_col=False)

    nomes = list(df_data.columns)

    id_rio = sorted(df_data['rio'].unique())
    col1, col2 = st.columns(2)
    rio = col1.radio('ID do rio - *a ser plotado*:', id_rio,
                    horizontal=True)
    
    df_data = df_data.loc[df_data['rio'] == rio]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    coll1, coll2 = st.columns(2)
    col21, col22 = coll2.columns(2)

    options_y = coll1.multiselect(
        "Y:",
        nomes,
        nomes[6])
            
    
    if 'data' in nomes:

        col2.write('')
        tipo = col2.toggle('Visualizar série temporal')
        
        if tipo == False:
        
            option_x = col21.selectbox(
                "X:",
                nomes, index=5)
                                
            id_dia = sorted(df_data['data'].unique())
            option_dia = col22.selectbox(
                "Data:",
                id_dia, index=0)
            
            fig.update_layout(title_text="Resultados do Rio " + str(rio) 
                            + ' - ' + str(option_dia),
                            title_font_color="teal")
            
            df_data = df_data.loc[df_data['data'] == option_dia]
            

        else:
            option_x = 'data'
            
            option_col_var = col21.selectbox(
                "Agrupar dados da coluna:",
                nomes, index=6)
            
            id_var = sorted(df_data[option_col_var].unique())
            option_var = col22.selectbox(
                "... com valores IGUAIS a:",
                id_var, index=0)
                                
            fig.update_layout(title_text="Resultados do Rio " + str(rio) 
                            + ' - ' + str(rio) + ': ' + str(rio),
                            title_font_color="teal")
            
            df_data = df_data.loc[df_data[option_col_var] == option_var]
    

    else:
        fig.update_layout(title_text="Resultados do Rio " + str(rio),
                            title_font_color="teal")
        
        option_x = col21.selectbox(
            "X:",
            nomes, index=5)
        
    for i in range(len(options_y)):
        fig.add_trace(go.Scatter(x=df_data[option_x], y=df_data[options_y[i]],
                                    name=options_y[i]))

    fig.update_xaxes(minor=dict(ticklen=3, tickcolor="black"))
    fig.update_yaxes(minor=dict(ticklen=3, tickcolor="black"))
    fig.update_layout(
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=1,
                    xanchor="right",
                    x=0.95),
        xaxis=dict(title=option_x, ticklen=4, tickcolor="black", showgrid=True, showline=True),
        yaxis=dict(showline=True, tickcolor="black", ticklen=4))
    
    st.plotly_chart(fig, use_container_width=True)

    st.write(df_data)
