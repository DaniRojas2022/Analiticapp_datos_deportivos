import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import html, dcc, Output, Input, callback
from sklearn.linear_model import PoissonRegressor
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import FunctionTransformer


dash.register_page(__name__)

resumenPartido = pd.read_csv(r'C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\resumenPartido.csv')
resumenPartido['disparoPuerta'] =   resumenPartido.apply(lambda x: x['gol'] if x['gol'] > 0 and x['disparoPuerta'] == 0 else x['disparoPuerta'], axis=1)
infoPartido = pd.read_csv(r'C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\factPartido.csv')
estadisticaPartido = pd.read_csv(r'C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\factEstadisticaPartido.csv')
equipo = pd.read_csv(r'C:\Users\daniel.rojas\Documents\FutbolAnalytics\FutbolAnalytics\data\dimEquipo.csv')

#consolidado informacion para prediccion
model_data = pd.DataFrame(columns=['team', 'opponent', 'goals', 'home'])
tmp = estadisticaPartido[['fkEquipoLocal','fkEquipoVisitante','golLocal']].copy()
tmp.rename(columns={'fkEquipoLocal':'team'
                           ,'fkEquipoVisitante':'opponent'
                           ,'golLocal':'goals'
                           },inplace=True )
tmp['home'] = 1
tmp = tmp.reset_index()
model_data = pd.concat([model_data, tmp], axis=0)

tmp = estadisticaPartido[['fkEquipoVisitante', 'fkEquipoLocal','golVisitante']].copy()
tmp.rename(columns={'fkEquipoVisitante':'team'
                           ,'fkEquipoLocal':'opponent'
                           ,'golVisitante':'goals'
                           },inplace=True )
tmp['home'] = 0
tmp = tmp.reset_index()
model_data = pd.concat([model_data, tmp], axis=0)

model_data = model_data.reset_index()
model_data = model_data[['team','opponent', 'home', 'goals']]
model_data['goals'] = model_data['goals'].astype(int)

# Crea un modelo de regresión Poisson utilizando scikit-learn
pois_model = PoissonRegressor()
x = model_data[['home', 'team', 'opponent']]
y = model_data['goals']
pois_model.fit(x, y)

layout = html.Div([
    html.H5("Enfretamiento entre equipos", className="display-4", style={'textAlign':'center'}),
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div(html.H6('Elegir Equipo Local')),
                    html.Div(dcc.Dropdown(resumenPartido['equipo'].unique() ,'Liverpool',  id='equipo_local'))
                ])
            ]),
            dbc.Col([
                html.Div([
                    html.Div(html.H6('Elegir Equipo Visitante')),
                    html.Div(dcc.Dropdown(resumenPartido['equipo'].unique() ,'Brighton',  id='equipo_visitante'))
                ])
            ])
        ])
    ]),
    html.Br(),
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div(dcc.Graph(figure={}, id='graf_cantidad_enfretamientos'))
            ]),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Cantidad de Enfretamientos')),
                            html.Div(html.P(id='cantidad_enfretamientos'))
                        ])
                    ])  
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Goles Marcados Local')),
                            html.Div(html.P(id='gol_marcado_local'))
                        ])
                    ]),
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Goles Marcados Visitante')),
                            html.Div(html.P(id='gol_marcado_visitante'))
                        ])
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Disparos a Puerta Local')),
                            html.Div(html.P(id='disparo_puerta_local'))
                        ])
                    ]),
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Disparos a Puerta Visitante')),
                            html.Div(html.P(id='disparo_puerta_visitante'))
                        ])
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Tiros de Esquina Local')),
                            html.Div(html.P(id='tiro_esquina_local'))
                        ])
                    ]),
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Tiros de Esquina Visitante')),
                            html.Div(html.P(id='tiro_esquina_visitante'))
                        ])
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Faltas Realizadas Local')),
                            html.Div(html.P(id='faltas_local'))
                        ])
                    ]),
                    dbc.Col([
                        html.Div([
                            html.Div(html.P('Faltas Realizadas Visitante')),
                            html.Div(html.P(id='faltas_visitante'))
                        ])
                    ])
                ])
            ])
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div(html.P('Comparación indicadores', style={'textAlign':'center'})),
                    html.Div(dcc.Graph(figure={}, id='radar-polar'))
                ])
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div(html.P('Predicción Gol Local',  style={'textAlign':'center'})),
                    html.Div(html.P(id='prediccion_gol_local', style={'textAlign':'center'})),
                    html.Div(dcc.Graph(figure={}, id='gol_historico_local'))
                ])
            ]),
            dbc.Col([
                html.Div([
                    html.Div(html.P('Predicción Gol Visitante', style={'textAlign':'center'})),
                    html.Div(html.P(id='prediccion_gol_visitante', style={'textAlign':'center'})),
                    html.Div(dcc.Graph(figure={}, id='gol_historico_visitante'))
                ])
            ])
        ])
    ])
])

@callback(
        Output(component_id='gol_historico_visitante',component_property='figure'),
        Input(component_id='equipo_visitante',component_property='value')
)
def actualizarGolHistoricoVisitante(equipoVisitante):
    df = resumenPartido[['equipo','gol', 'fecha']].copy()
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df[(df.equipo==equipoVisitante) &(df.fecha > '2023-01-01')]
    figure = px.scatter(df, x='fecha', y='gol'
                        , trendline="rolling"
                        , trendline_options=dict(window=5)
                        ,title='Goles Marcados Visitante'
                        ,color_discrete_sequence=['#F2055C']
                        ,template='simple_white'
                        )
    return figure


@callback(
        Output(component_id='gol_historico_local',component_property='figure'),
        Input(component_id='equipo_local',component_property='value')
)
def actualizarGolHistoricoLocal(equipoLocal):
    df = resumenPartido[['equipo','gol', 'fecha']].copy()
    df['fecha'] = pd.to_datetime(df['fecha'])
    df = df[(df.equipo==equipoLocal) & (df.fecha > '2023-01-01')]
    figure = px.scatter(df, x='fecha', y='gol'
                        , trendline="rolling"
                        , trendline_options=dict(window=5)
                        ,title='Goles Marcados Local'
                        ,color_discrete_sequence=['#340040']
                        ,template='simple_white'
                        )
    return figure

@callback(
        Output(component_id='prediccion_gol_visitante',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarPrediccionGolLocal(equipoLocal, equipoVisitante):
    skEquipoLocal = equipo[equipo.equipoDesc==equipoLocal].values[0][0]
    skEquipoVisitante = equipo[equipo.equipoDesc==equipoVisitante].values[0][0]
    prediccionVisitante = pois_model.predict(pd.DataFrame({'home': [0], 'team': [skEquipoVisitante], 'opponent': [skEquipoLocal]}))
    prediccionVisitante = round(prediccionVisitante[0],3)
    return prediccionVisitante

@callback(
        Output(component_id='prediccion_gol_local',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarPrediccionGolLocal(equipoLocal, equipoVisitante):
    skEquipoLocal = equipo[equipo.equipoDesc==equipoLocal].values[0][0]
    skEquipoVisitante = equipo[equipo.equipoDesc==equipoVisitante].values[0][0]
    prediccionLocal = pois_model.predict(pd.DataFrame({'home': [1], 'team': [skEquipoLocal], 'opponent': [skEquipoVisitante]}))
    prediccionLocal = round(prediccionLocal[0],3)
    return prediccionLocal

@callback(
        Output(component_id='faltas_visitante',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarFaltaVisitante(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['faltaVistante'].sum())
    return txt

@callback(
        Output(component_id='faltas_local',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarFaltaLocal(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['faltaLocal'].sum())
    return txt

@callback(
        Output(component_id='tiro_esquina_visitante',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarTiroEsquinaVisitante(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['TiroEsquinaVisitante'].sum())
    return txt

@callback(
        Output(component_id='tiro_esquina_local',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarTiroEsquinaLocal(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['TiroEsquinaLocal'].sum())
    return txt

@callback(
        Output(component_id='disparo_puerta_visitante',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarDisparoPuertaVisitante(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['disparoPuertaVisitante'].sum())
    return txt

@callback(
        Output(component_id='disparo_puerta_local',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarDisparoPuertaLocal(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['disparoPuertaLocal'].sum())
    return txt

@callback(
        Output(component_id='gol_marcado_visitante',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarGolMarcadoVisitante(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['golVisitante'].sum())
    return txt

@callback(
        Output(component_id='gol_marcado_local',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarGolMarcadoLocal(equipoLocal, equipoVisitante):
    df = estadisticaPartido[(estadisticaPartido.equipoLocal==equipoLocal) & (estadisticaPartido.equipoVisitante==equipoVisitante)]
    txt = str(df['golLocal'].sum())
    return txt


@callback(
        Output(component_id='graf_cantidad_enfretamientos',component_property='figure'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def graficaCantidadEnfretamientos(equipoLocal, equipoVisitante):
    df = infoPartido[(infoPartido.equipoLocal==equipoLocal) & (infoPartido.equipoVisitante==equipoVisitante)]
    df = df.groupby('resultado', as_index=False)['skPartido'].count()
    figure=px.pie(df, values='skPartido', names='resultado'
                  ,width=370
                  ,height=350
                  ,hole=0.5
                  ,color_discrete_sequence= ['#340040','#F2055C','#05F26C']
                                 )
    figure.update_layout(legend_title_text='Victoria')
    return figure


@callback(
        Output(component_id='cantidad_enfretamientos',component_property='children'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarCantidadEnfretamientos(equipoLocal, equipoVisitante):
    txt = str(len(infoPartido[(infoPartido.equipoLocal==equipoLocal) & (infoPartido.equipoVisitante==equipoVisitante)]))
    return txt

@callback(
        Output(component_id='radar-polar',component_property='figure'),
        [Input(component_id='equipo_local',component_property='value'),
        Input(component_id='equipo_visitante',component_property='value')]
)
def actualizarRadar(equipoLocal, equipoVisitante):
    resumenPartido['atajada'] = resumenPartido['atajada'].replace(-1,0)
    resumenPartido['Efectividad Arquero'] = resumenPartido.apply(lambda x: 1 if x['atajada'] == 0 and x['disparoPuertaEnContra'] == 0 else (x['atajada'] / x['disparoPuertaEnContra']), axis=1 )
    #resumenPartido['Efectividad Arquero'] = resumenPartido['atajada'] / resumenPartido['disparoPuertaEnContra']
    resumenPartido['Efectividad Derribo'] = resumenPartido['derriboConseguido'] / resumenPartido['derribo']
    resumenPartido['Efectividad Disparo'] = resumenPartido['gol'] / resumenPartido['disparoPuerta']
    
    polar = resumenPartido[['equipo', 'Efectividad Arquero', 'Efectividad Derribo', 'Efectividad Disparo'
                            , 'posesionBalon', 'precisionPase']].copy()
    polar.fillna(0, inplace=True)
    polar = polar.groupby('equipo', as_index=False)[['Efectividad Arquero','Efectividad Derribo','Efectividad Disparo'
                                                    , 'posesionBalon', 'precisionPase']].mean()
    polar.rename(columns={'posesionBalon': 'Posesion Balon',
                          'precisionPase': 'Precision Pase'}, inplace=True)
    polar.fillna(0, inplace=True)
    polar = polar.melt(
            id_vars=['equipo'],
            var_name='metrica',
            value_name='valor')
    polar['valor'] =  round(polar['valor'] * 100,1)

    df = polar[(polar.equipo== equipoLocal) | (polar.equipo== equipoVisitante) ]
    figure = px.line_polar(df, r='valor', theta='metrica'
                           , line_close = True
                           , color='equipo'
                           , color_discrete_sequence=['#F2055C','#05F26C'])
    figure.update_traces(fill = 'toself')
    return figure