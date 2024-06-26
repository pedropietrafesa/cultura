#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import plotly.graph_objects as go
import openpyxl

# Dados
df = pd.read_excel("https://github.com/pedropietrafesa/cultura/raw/main/PAAR2024-05-13_15_48_09.xlsx")
df1 = pd.read_excel("https://github.com/pedropietrafesa/cultura/raw/main/Formulario_de_Inscricao_Circula2024.xlsx")

# Removendo a coluna 'Área'
df = df.drop('Participacao', axis=1)
# Removendo as colunas 'Área' e 'PIB'
df1 = df1.drop(['Quais são as suas dúvidas em relação à LPG?', 'Quais são as suas dúvidas em relação à PNAB?'], axis=1)

estados_unicos = sorted(df['UF'].unique())
estados_unicos1 = sorted(df1['UF'].unique())

# Inicialização do app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.title = 'Dashboards de monitoramento Lei Paulo Gustavo e a Política Nacional Aldir Blanc'

# Layout principal com navegação
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dbc.Nav(
            [
                dbc.NavLink("Planos ", href="/", active="exact"),
                dbc.NavLink("Roda de Dúvidas", href="/pagina-2", active="exact"),
            ],
            pills=True,
        ),
    ]),
    html.Div(id='page-content')
])

# Página 1
page_1_layout = html.Div([
    # Linha 1: Título e Dropdown
    html.Div([
        html.Div([
            html.H1("Monitoramento do Cadastro dos Planos Municipais - Valores (R$) ", style={'textAlign': 'center'})
        ], style={'width': '70%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Selecione um Estado:"),
            dcc.Dropdown(
                id='estado-dropdown1',
                options=[{'label': estado, 'value': estado} for estado in estados_unicos],
                value='AC'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # Linha 2: Gráficos de Barra
    html.Div([
        html.Div([
            dcc.Graph(id='total-investimento-estado')
        ], style={'width': '40%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='investimento-plano-cultura')
        ], style={'width': '60%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # Linha 3: Gráficos de Fundo de Cultura e Cargos dos Responsáveis
    html.Div([
        html.Div([
            dcc.Graph(id='investimento-fundo-cultura')
        ], style={'width': '70%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='cargo-responsavel-envio')
        ], style={'width': '30%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # Linha 4: Tabela de Dados
    html.Div([
        dash_table.DataTable(id='table-planos')
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '20px'})
])

# Página 2
page_2_layout = html.Div([
    # Linha 1: Título e Dropdown
    html.Div([
        html.Div([
            html.H1("Monitoramento das Rodas de Conversas para Retirar Dúvidas", style={'textAlign': 'center'})
        ], style={'width': '70%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Selecione um Estado:"),
            dcc.Dropdown(
                id='estado-dropdown2',
                options=[{'label': estado, 'value': estado} for estado in estados_unicos1],
                value='AC'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # Linha 2: Gráficos de Fundo de Cultura e Cargos dos Responsáveis
    html.Div([
        html.Div([
            dcc.Graph(id='orgao')
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='cargo')
        ], style={'width': '50%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # Linha 3: Tabela de Dados
    html.Div([
        dash_table.DataTable(id='table-duvidas')
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '20px'})
])

# Update page content based on URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/pagina-2':
        return page_2_layout
    else:
        return page_1_layout

# Callback para a primeira página
@app.callback(
    [Output('total-investimento-estado', 'figure'),
     Output('investimento-plano-cultura', 'figure'),
     Output('investimento-fundo-cultura', 'figure'),
     Output('cargo-responsavel-envio', 'figure'),
     Output('table-planos', 'data'),
     Output('table-planos', 'columns')],
    [Input('estado-dropdown1', 'value')]
)
def update_dashboard(estado_selecionado):
    df_filtrado = df[df['UF'] == estado_selecionado]
    
    # Gráfico de barras horizontal com total de investimentos por estado
    total_investimento = df.groupby('UF')['Valor'].sum().reset_index()
    fig_total_investimento = go.Figure(data=go.Bar(x=total_investimento['Valor'], y=total_investimento['UF'], orientation='h'))
    fig_total_investimento.update_layout(
        title='Total de Recursos Propostos nos Planos Municipais por Estado',
        xaxis_title='Valor em R$',
        yaxis_title='Estado',
        font=dict(size=8)
    )
    
    # Gráfico de barras com investimentos por município e plano de cultura
    color_map = {
        'Em elaboração': 'blue',
        'Não': 'red',
        'Sim': 'green'
    }
    
    fig_investimento_plano = go.Figure(data=[
        go.Bar(
            x=df_filtrado[df_filtrado['Plano'] == categoria]['Recebedor'],
            y=df_filtrado[df_filtrado['Plano'] == categoria]['Valor'],
            name=categoria,
            marker_color=color_map.get(categoria, 'gray')
        ) for categoria in df_filtrado['Plano'].unique()
    ])
    fig_investimento_plano.update_layout(
        title=f'Valores Propostos pelos Municípios de {estado_selecionado} (Possui Plano de Cultura?)',
        xaxis_title='Município',
        yaxis_title='Valor em R$',
        font=dict(size=7),
        barmode='stack',
        showlegend=True
    )

    # Gráfico de barras com investimentos por município e fundo de cultura
    fig_investimento_fundo = go.Figure(data=[
        go.Bar(
            x=df_filtrado[df_filtrado['Fundo'] == categoria]['Recebedor'],
            y=df_filtrado[df_filtrado['Fundo'] == categoria]['Valor'],
            name=categoria,
            marker_color=color_map.get(categoria, 'gray')
        ) for categoria in df_filtrado['Fundo'].unique()
    ])
    fig_investimento_fundo.update_layout(
        title=f'Valores Propostos pelos Municípios de {estado_selecionado} (Possui Fundo de Cultura?)',
        xaxis_title='Município',
        yaxis_title='Valor em R$',
        font=dict(size=7),
        barmode='stack',
        showlegend=True
    )
    
    # Gráfico de barras com quantidade de envio do plano por cargo
    cargo_count = df_filtrado['Cargo_Cat'].value_counts().reset_index()
    cargo_count.columns = ['Cargo', 'Quantidade']
    fig_cargo_responsavel = go.Figure(data=go.Bar(x=cargo_count['Cargo'], y=cargo_count['Quantidade']))
    fig_cargo_responsavel.update_layout(
        title=f'Responsável pelo Envio dos Planos por Cargo: {estado_selecionado}',
        xaxis_title='Cargo',
        yaxis_title='Quantidade',
        font=dict(size=10)
    )
    
    # Tabela de Dados
    table_data = df_filtrado.to_dict('records')
    table_columns = [{"name": i, "id": i} for i in df_filtrado.columns]
    
    return fig_total_investimento, fig_investimento_plano, fig_investimento_fundo, fig_cargo_responsavel, table_data, table_columns

# Callback para a segunda página
@app.callback(
    [Output('orgao', 'figure'),
     Output('cargo', 'figure'),
     Output('table-duvidas', 'data'),
     Output('table-duvidas', 'columns')],
    [Input('estado-dropdown2', 'value')]
)
def update_dashboard1(estado_selecionado):
    df1_filtrado = df1[df1['UF'] == estado_selecionado]

    # Gráfico de barras com os órgãos
    orgao_count = df1_filtrado['órgão'].value_counts().reset_index()
    orgao_count.columns = ['Órgão', 'Quantidade']
    fig_orgao = go.Figure(data=go.Bar(x=orgao_count['Órgão'], y=orgao_count['Quantidade']))
    fig_orgao.update_layout(
        title=f'Instituição que trabalha: {estado_selecionado}',
        xaxis_title='Órgão',
        yaxis_title='Quantidade',
        font=dict(size=8)
    )

    # Gráfico de barras com os órgãos
    cargo_count = df1_filtrado['Cargo_Cat'].value_counts().reset_index()
    cargo_count.columns = ['Cargo', 'Quantidade']
    fig_cargo = go.Figure(data=go.Bar(x=cargo_count['Cargo'], y=cargo_count['Quantidade']))
    fig_cargo.update_layout(
        title=f' Cargo de quem tirou dúvidas: {estado_selecionado}',
        xaxis_title='Cargo',
        yaxis_title='Quantidade',
        font=dict(size=8)
    )

    # Tabela de Dados
    table_data = df1_filtrado.to_dict('records')
    table_columns = [{"name": i, "id": i} for i in df1_filtrado.columns]

    return fig_orgao, fig_cargo, table_data, table_columns

if __name__ == '__main__':
    app.run_server(debug=True)

