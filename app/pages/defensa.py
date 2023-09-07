import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, dcc, Output, Input, callback
from datetime import datetime

dash.register_page(__name__)

resumenPartido = pd.read_csv(r'C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\resumenPartido.csv')
resumenPartido['fecha'] = resumenPartido['fecha'].apply(lambda x: datetime.strptime(x, '%m/%d/%Y').date() )
resumenPartido['anio'] = resumenPartido['fecha'].apply(lambda x: x.year)
resumenPartido.sort_values(by=['fecha'], inplace=True)

layout = html.Div([
    html.H5("Estadisticas en Defensa", className="display-4", style={'textAlign':'center'}),
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col(dcc.Dropdown(resumenPartido['equipo'].unique() ,'Liverpool',  id='elegir_equipo_defensa')),
            dbc.Col([
                html.Div([
                    html.Div(html.H6(id='efectividad_derribo', style={'textAlign':'center'})),
                    html.Div(html.H6('Efectividad Derribo', style={'textAlign':'center'}))
                ])
            ]),
            dbc.Col([
                html.Div([
                    html.Div(html.H6(id='efectividad_arquero', style={'textAlign':'center'})),
                    html.Div(html.H6('Efectividad Arquero', style={'textAlign':'center'}))
                ])
            ]),
            dbc.Col([
                html.Div([
                    html.Div(html.H6(id='gol_recibido', style={'textAlign':'center'})),
                    html.Div(html.H6('Promedio Gol Recibido', style={'textAlign':'center'}))
                ])
            ])
        ])
    ]),
    html.Br(),
    html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(figure={}, id ='disparos_encontra'))
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure={}, id="falta_intercepcion")),
            dbc.Col(dcc.Graph(figure={}, id='tarjetas_amarillas'))
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure={},id='tipo_derribo'))
        ])

    ])
])

@callback(
    Output(component_id='disparos_encontra',component_property='figure'),
    Input(component_id='elegir_equipo_defensa',component_property='value')
)
def actualizarDisparoEnContra(equipo):
    if equipo is None:
        df = resumenPartido[['disparoPuertaEnContra', 'golRecibido','condicion']]
    else:
        df = resumenPartido[resumenPartido.equipo==equipo][['disparoPuertaEnContra', 'golRecibido','condicion']]
    figure = px.scatter(df, x='disparoPuertaEnContra', y= 'golRecibido'
                        ,title='Disparos a Puerta en Contra vs Gol Recibidos'
                        ,trendline="ols"
                        ,facet_col='condicion'
                        ,color='condicion'
                        ,color_discrete_map={'Local':'#340040'
                                          ,'Visitante':'#F2055C'}
                        ,labels={'disparoPuertaEnContra':'Disparos En Contra'
                                 ,'golRecibido':'Goles Recibido'}
                        ,template='simple_white'
                        )
    figure.update_layout(legend_title_text='Condición')
    return figure

@callback(
    Output(component_id='tipo_derribo',component_property='figure'),
    Input(component_id='elegir_equipo_defensa',component_property='value')
)
def actualizarTipoDerribo(equipo):
    if equipo is None:
        df = resumenPartido
    else:
        df = resumenPartido[resumenPartido.equipo==equipo]
    
    figure = px.scatter(df, x='fecha', y=['derriboDefensa', 'derriboCentro', 'derriboAtaque']
                        , title='Tipos Derribo'
                        , labels={'fecha':'Fecha'
                                  ,'value':''}
                        ,color_discrete_map={'derriboDefensa':'#07F2F2'
                                             ,'derriboCentro':'#63F268'
                                             ,'derriboAtaque':'#F9F25A'}
                        ,template='simple_white'
                        , marginal_y='box')
    return figure


@callback(
    Output(component_id='tarjetas_amarillas',component_property='figure'),
    Input(component_id='elegir_equipo_defensa',component_property='value')
)
def actualizarTarjetaRecibida(equipo):
    if equipo is None:
        df = resumenPartido[['fecha','tarjetaAmarilla','condicion']]
    else:
        df = resumenPartido[resumenPartido.equipo==equipo][['fecha','tarjetaAmarilla','condicion']]
    
    figure = px.line(df, x='fecha', y='tarjetaAmarilla'
                     , color='condicion'
                     ,title='Tarjetas Amarillas Recibidas'
                     ,labels={'fecha':'Fecha'
                              ,'tarjetaAmarilla':''}
                     ,color_discrete_map={'Local':'#340040'
                                          ,'Visitante':'#F2055C'}
                     ,height=600
                     ,width=700
                     ,template='simple_white'                            
                    )
    figure.update_layout(legend_title_text='Condición')
    return figure

@callback(
    Output(component_id='falta_intercepcion',component_property='figure'),
    Input(component_id='elegir_equipo_defensa',component_property='value')
)
def actualizarFaltaIntercepcion(equipo):
    if equipo is None:
        df = resumenPartido[['anio', 'falta', 'intercepcion']]
    else:
        df = resumenPartido[resumenPartido.equipo==equipo][['anio', 'falta', 'intercepcion']]
    df = df.groupby(['anio'], as_index=False)[['falta','intercepcion']].mean()
    figure = px.bar(df,x='anio',y=['falta', 'intercepcion']
                    , barmode = 'group'
                    ,title='Intercepción vrs Faltas Cometidas'
                    ,labels={'anio':'Año'
                             ,'value': ''}
                    ,color_discrete_map={'falta':'#F9F25A'
                                         ,'intercepcion':'#63F268'}
                    ,height=600
                    ,width=500
                    ,template='simple_white')
    figure.update_layout(legend_title_text='Tipo Jugada')
    return figure

@callback(
    Output(component_id='gol_recibido',component_property='children'),
    Input(component_id='elegir_equipo_defensa',component_property='value')
)
def actualizarGolRecibido(equipo):
    resumen = resumenPartido.groupby('equipo', as_index=False)[['golRecibido']].mean()
    resumen.fillna(0,inplace=True)

    if equipo is None:
        valor = round(resumen['golRecibido'].mean(),2)
        txt = str(valor) 
    else:
        valor = round(resumen[resumen.equipo==equipo].values[0][1],2)
        txt = str(valor) 
    return txt

@callback(
    Output(component_id='efectividad_arquero',component_property='children'),
    Input(component_id='elegir_equipo_defensa',component_property='value')
)
def actualizarEfectividadArquero(equipo):
    resumenPartido['atajada'] = resumenPartido['atajada'].replace(-1,0)
    resumenPartido['efectividadArquero'] = resumenPartido.apply(lambda x: 1 if x['atajada'] == 0 and x['disparoPuertaEnContra'] == 0 else (x['atajada'] / x['disparoPuertaEnContra']) * 100, axis=1 )
    #resumenPartido['efectividadArquero'] = (resumenPartido['atajada'] / resumenPartido['disparoPuertaEnContra']) * 100
    resumen = resumenPartido.groupby('equipo', as_index=False)[['efectividadArquero']].mean()
    resumen.fillna(0,inplace=True)

    if equipo is None:
        valor = round(resumen['efectividadArquero'].mean(),2)
        txt = str(valor) + "%"
    else:
        valor = round(resumen[resumen.equipo==equipo].values[0][1],2)
        txt = str(valor) + "%"
    return txt


@callback(
    Output(component_id='efectividad_derribo',component_property='children'),
    Input(component_id='elegir_equipo_defensa',component_property='value')
)
def actualizarEfectividadDerribo(equipo):
    resumenPartido['efectividadDerribo'] = (resumenPartido['derriboConseguido'] / resumenPartido['derribo']) * 100
    resumen = resumenPartido.groupby('equipo', as_index=False)[['efectividadDerribo']].mean()
    resumen.fillna(0,inplace=True)

    if equipo is None:
        valor = round(resumen['efectividadDerribo'].mean(),2)
        txt = str(valor) + "%"
    else:
        valor = round(resumen[resumen.equipo==equipo].values[0][1],2)
        txt = str(valor) + "%"
    return txt
