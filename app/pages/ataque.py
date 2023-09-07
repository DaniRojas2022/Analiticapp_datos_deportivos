import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input
from datetime import datetime

dash.register_page(__name__)

resumenPartido = pd.read_csv(r'C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\resumenPartido.csv')
resumenPartido['fecha'] = resumenPartido['fecha'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y').date() )
resumenPartido['anio'] = resumenPartido['fecha'].apply(lambda x: x.year)
resumenPartido.sort_values(by=['fecha'], inplace=True)
resumenPartido['disparoPuerta'] =   resumenPartido.apply(lambda x: x['gol'] if x['gol'] > 0 and x['disparoPuerta'] == 0 else x['disparoPuerta'], axis=1)
resumenPartido['efectividadDisparo'] = (resumenPartido['gol'] / resumenPartido['disparoPuerta']) * 100
resumenPartido['precisionPase'] = resumenPartido['precisionPase']*100

resumen = resumenPartido.groupby(['equipo'], as_index=False)[['efectividadDisparo','precisionPase','gol']].mean()
resumen['gol'] = round(resumen['gol'],0)
resumen['efectividadDisparo'] = round(resumen['efectividadDisparo'],2)
resumen['precisionPase'] = round(resumen['precisionPase'],2) 
resumen.fillna(0,inplace=True)



layout = html.Div([
    html.H5("Estadistica por Equipo en Ataque", className="display-4", style={'textAlign':'center'}),
    html.Hr(),
    html.Div(
    [
        dbc.Row([
            dbc.Col(dcc.Dropdown(resumenPartido['equipo'].unique() ,'Liverpool',  id='elegir_equipo')),
            dbc.Col([
                html.Div([
                    html.Div(html.H6(id='efectividad_disparo', style={'textAlign':'center'})),
                    html.Div(html.H6("Efectividad Disparo", style={'textAlign':'center'}))
                ])
            ]),
            dbc.Col([
                html.Div([
                    html.Div(html.H6(id='precision_pase', style={'textAlign':'center'})),
                    html.Div(html.H6("Precisión Pase", style={'textAlign':'center'}))
                ])
            ]),
            dbc.Col([
                html.Div([
                    html.Div(html.H6(id='gol', style={'textAlign':'center'})),
                    html.Div(html.H6("Promedio Gol", style={'textAlign':'center'}))
                ])
            ])
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id='promedio_gol')),
        dbc.Col(dcc.Graph(figure={}, id='promedio_posesion'))
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id='gol_marcado'))
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(figure={}, id='efectividad_pase'))
    ])
])

@callback(
        Output(component_id='efectividad_pase',component_property='figure'),
        Input(component_id='elegir_equipo',component_property='value')
)
def actualizarPase(equipo):
    if equipo is None:
        dfFiltro = resumenPartido
    else:
        dfFiltro = resumenPartido[resumenPartido.equipo == equipo]
    dfFiltro = dfFiltro[['efectividadPaseCorto','efectividadPaseMedioIntentado','efectividadPaseLargo']]
    figure = px.histogram(dfFiltro
                          ,x=['efectividadPaseCorto','efectividadPaseMedioIntentado','efectividadPaseLargo']
                          ,title='Efectividad por Tipo de Pase'
                          ,color_discrete_map={
                              'efectividadPaseCorto':'#07F2F2'
                              ,'efectividadPaseMedioIntentado':'#63F268'
                              ,'efectividadPaseLargo':'#F9F25A'}
                          ,labels={'count':''
                                   ,'value':'Efectividad'}
                          ,template='simple_white')
    return figure


@callback(
        Output(component_id='gol_marcado',component_property='figure'),
        Input(component_id='elegir_equipo',component_property='value')
)
def actualizarGolMarcado(equipo):
    if equipo is None:
        dfFiltro = resumenPartido
    else:
        dfFiltro = resumenPartido[resumenPartido.equipo == equipo]
    
    resumenGol = dfFiltro.groupby(['equipo'], as_index=False)[['gol','golRecibido']].mean()
    resumenGol['gol'] = resumenGol['gol'].apply(lambda x: round(x,2))
    resumenGol['golRecibido'] = resumenGol['golRecibido'].apply(lambda x: round(x,2))
    resumenGol = resumenGol.sort_values(by='gol', ascending=False)[:7]
    figure = px.bar(resumenGol, y='equipo', x=['gol','golRecibido']
                    ,title='Gol Marcado y Recibido'
                    ,text_auto=True
                    ,color_discrete_map={'gol':'#07F2F2'
                                         ,'golRecibido':'#F4446D'}
                    ,labels={'equipo':'Equipo'
                             ,'value':'Gol Marcado - Gol Recibido'}
                    ,template='simple_white')
    figure.update_layout(legend=dict(orientation="h",
                                     yanchor="bottom",
                                     y=1.02,
                                     xanchor="left",
                                     x=1), legend_title_text='Gol')
    return figure

@callback(
        Output(component_id='promedio_posesion',component_property='figure'),
        Input(component_id='elegir_equipo',component_property='value')
)
def actualizarPosesion(equipo):
    if equipo is None:
        dfFiltro = resumenPartido
    else:
        dfFiltro = resumenPartido[resumenPartido.equipo == equipo]  
    avgPosesion =  dfFiltro.groupby(['anio', 'condicion'], as_index=False )['posesionBalon'].mean()
    avgPosesion['posesionBalon'] = avgPosesion['posesionBalon'].apply(lambda x: x * 100)

    figure = px.bar(avgPosesion, x='anio', y='posesionBalon'
                    ,color='condicion'
                    ,title='Promedio Posesión del Balón por Año'
                    ,text_auto=True
                    ,color_discrete_map={'Local':'#340040'
                                            ,'Visitante':'#F2055C'}
                    ,labels={'anio':'Año'
                                ,'posesionBalon':'Posesión Balón'}
                    ,height=550
                    ,width=570
                    ,template='simple_white').update_layout(legend_title_text='Condición')
    return figure

@callback(
        Output(component_id='promedio_gol',component_property='figure'),
        Input(component_id='elegir_equipo',component_property='value')
)
def actualizarPromedioGol(equipo):
    if equipo is None:
        dfFiltro = resumenPartido[['condicion','gol']]
    else:
        dfFiltro = resumenPartido[resumenPartido.equipo == equipo][['condicion','gol']]
    figure = px.box(dfFiltro, x='condicion', y='gol'
                    ,color='condicion'
                    ,points='all'
                    ,color_discrete_map={'Local':'#340040',
                                        'Visitante':'#F2055C'}
                    ,labels={'condicion':'Año',
                            'gol':'Gol'}
                    ,height=550
                    ,width=670
                    ,template='simple_white'
                    )
    figure.update_layout(legend_title_text='Condición')
    return figure

@callback(
    Output(component_id='efectividad_disparo',component_property='children'),
    Input(component_id='elegir_equipo',component_property='value')
)
def actualizarEfectividadDisparo(equipo):
    if equipo is None:
        valor = round(resumen['efectividadDisparo'].mean(),2)
        txt = str(valor) + "%"
    else:
        valor = resumen[resumen.equipo==equipo].values[0][1]
        txt = str(valor) + "%"
    return txt

@callback(
    Output(component_id='precision_pase',component_property='children'),
    Input(component_id='elegir_equipo',component_property='value')
)
def actualizarPrecisionPase(equipo):
    if equipo is None:
        valor = round(resumen['precisionPase'].mean(),2)
        txt = str(valor) + "%"
    else:
        valor = resumen[resumen.equipo==equipo].values[0][2]
        txt = str(valor) + "%"
    return txt

@callback(
    Output(component_id='gol',component_property='children'),
    Input(component_id='elegir_equipo',component_property='value')
)
def actualizarPromedioGol(equipo):
    if equipo is None:
        valor = round(resumen['gol'].mean())
        txt = str(valor)
    else:
        valor = round(resumen[resumen.equipo==equipo].values[0][3])
        txt = str(valor)
    return txt