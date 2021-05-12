#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 10:38:40 2021

@author: leo
"""

import seaborn as sns
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px

import pandas as pd

from code_and_stuff.data_handling.handle_data import get_anime,get_users_ratings
from code_and_stuff.data_handling.handle_data import get_virgin_data, drop_users_with_too_many_items
from code_and_stuff.data_handling.handle_data import replace_rating_with_0_and_1, transform_ratings
from code_and_stuff.data_handling.handle_data import get_titles, get_my_ratings
from code_and_stuff.data_handling.handle_data import drop_users_with_high_proportion_of_ratings

'https://cdn.myanimelist.net'  # should replace image_url

def get_genres_area_graph():
    gr=anime_data.iloc[:, 8:]
    for col in gr.columns:
        idx = gr.loc[gr[col] == 1].index
        c=pd.Series(col,index=idx, name=col)
        gr[col] = c
    genres=pd.concat([gr[col] for col in gr.columns]).dropna()
    genres.name = 'genres'
    genres = genres.to_frame().join(anime_data.Year).groupby('Year')['genres'].value_counts()
    genres.name = 'genres_count'
    genres = genres.reset_index()
    return px.area(genres,x='Year', y='genres_count', color='genres')

COLUMN_GENRES_INDEX = 8
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

anime_data = get_anime()
rate = get_users_ratings()
rate_exist_but_no_info_about_anime = rate[~rate.item.isin(anime_data.index)].index
rate.drop(index=rate_exist_but_no_info_about_anime, inplace=True)

transformed_rate = transform_ratings(rate)
# df=gr.groupby('Year', as_index=False).agg(sum)
data = rate.copy()
rc = data.rating.value_counts().sort_index(ascending=False).to_frame().reset_index()
rc.columns = ['rating', 'count']

fig = px.bar(rc, x=rc['rating'], y=rc['count'], barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children=[
        html.H1(f'mean rating for all anime: {data.rating.mean()}', id='mean'),
        html.H2(f'total rates: {data.rating.count()}'),
        dcc.Graph(
            id='graph-rate-count',
            figure=fig,
            )], id='mean_and_graph'),
    html.Br(),
    html.Div([
        "Transform data rating",
        dcc.RadioItems(
            options=[
                {'label': '1-10', 'value': 'full_rate'},
                {'label': '1-5', 'value': 'transformed_rate'}
            ],
            value='full_rate',
            id='transform'
        )
        ]),
        html.Br(),
    html.Div([
        html.H1('genres area plot'),
        dcc.Graph(
            id='area_plot',
            figure=get_genres_area_graph(),
            style={'display': 'inline-block'},
            ),
        ]),
])

# ehh
@app.callback(
    Output(component_id='mean', component_property='children'),
    Output(component_id='graph-rate-count', component_property='figure'),
    Input(component_id='transform', component_property='value'),
)
def update_graph(transform_data):
    df = data
    if transform_data == 'transformed_rate':
        #df = transform_ratings(data)
        df = transformed_rate
    rc = df.rating.value_counts().sort_index(ascending=False).to_frame().reset_index()
    rc.columns = ['rating', 'count']
    fig = px.bar(rc, x=rc['rating'], y=rc['count'], barmode="group")
    return f'mean rating for all anime: {df.rating.mean()}', fig

# how to update mean


if __name__ == '__main__':
    app.run_server(debug=True)
