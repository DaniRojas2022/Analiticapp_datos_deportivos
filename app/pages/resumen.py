import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime

dash.register_page(__name__)

# = pd.read_csv('C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\resumenPartido.csv')
infoPartido = pd.read_csv(r'C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\factPartido.csv')
infoPartido['fecha'] = infoPartido['fecha'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y').date() )
infoPartido['anio'] = infoPartido['fecha'].apply(lambda x: x.year)
infoPartido.sort_values(by=['fecha'], inplace=True)

dfpie = infoPartido.groupby(['resultado'], as_index=False)['skPartido'].count()
dfline = infoPartido.groupby(['anio','resultado'], as_index=False)['skPartido'].count()

dfResul = infoPartido.groupby(['equipoLocal','resultado'], as_index=False)['skPartido'].count()
dfBarGanan = dfResul[dfResul['resultado'] == 'Local'].sort_values(by='skPartido', ascending=False)[:7]
fig = px.bar(dfBarGanan, y='equipoLocal',x='skPartido'
             ,title='Equipo con más Victorias como Local'
             ,labels={
                 'equipoLocal':'Equipo',
                 'skPartido':'# Victorias Local'}
             ,text_auto=True
             ,template='simple_white')
fig.update_traces(marker_color='#340040')

dfResul = infoPartido.groupby(['equipoVisitante','resultado'], as_index=False)['skPartido'].count()
dfBarVisitante = dfResul[dfResul['resultado'] == 'Visitante'].sort_values(by='skPartido', ascending=False)[:7]

figVisistante = px.bar(dfBarVisitante, y='equipoVisitante',x='skPartido'
                       ,title='Equipo con más Victorias como Visitante'
                       ,labels={
                           'equipoVisitante':'Equipo',
                           'skPartido':'# Victorias Visitante'}
                        ,text_auto=True
                        ,template='simple_white')
figVisistante.update_traces(marker_color='#F2055C')

layout = html.Div([
    html.H5("Resultado General Partidos de Futbol", className="display-4", style={'textAlign':'center'}),
    html.Hr(),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=px.pie(dfpie, values='skPartido', names='resultado'
                                        ,title='Distribucción Resultados'
                                        ,hole=0.5
                                        ,height=600
                                        ,width=420
                                        ,color=['Local', 'Visitante', 'Empate']
                                        ,color_discrete_map={'Local':'#340040',
                                                             'Visitante':'#F2055C',
                                                             'Empate':'#05F26C'}))),
        dbc.Col(dcc.Graph(figure=px.line(dfline, x='anio',y='skPartido'
                                         ,color='resultado'
                                         ,title='Historico Resultados'
                                         ,markers = True
                                         #,height=600
                                         #,width=550
                                         ,color_discrete_map={'Local':'#340040',
                                                              'Visitante':'#F2055C',
                                                              'Empate':'#05F26C'}
                                         ,labels={
                                             'skPartido':'# Partidos',
                                             'anio':'Mes - Año'
                                         }
                                         ,template='simple_white')
                                                              ))
    
    ]),
    html.Hr(),
    html.Div(children='Resultados por Equipo'),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig )),
        dbc.Col(dcc.Graph(figure=figVisistante))
    ])
])