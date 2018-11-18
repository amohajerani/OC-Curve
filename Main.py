# this code assumes the population size is infinite
from math import factorial as f
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import io
import base64
from scipy import stats
import matplotlib.pyplot as plt
import flask
import os
import matplotlib.mlab as mlab
from scipy.stats import norm
import statsmodels.api as sm
def Pa(n,c,p): # probability of acceptance for a given lot proportion defective p
    res=0
    p=p/100
    for X in range(c+1):
        delta=f(n)/(f(X)*f(n-X))*p**X*(1-p)**(n-X)
        res+=delta
    return res
css_directory = os.getcwd()
stylesheets = ['Style.css']
static_css_route = '/static/'

app = dash.Dash(__name__)

@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in stylesheets:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    return flask.send_from_directory(css_directory, stylesheet)

for stylesheet in stylesheets:
    app.css.append_css({"external_url": "/static/{}".format(stylesheet)})

app.layout=html.Div([
    html.Div([html.H1(children="Attribute OC Curves")], style={"text-align":"center"}),
    html.Div([
    html.H4(children="Number of samples"),
    dcc.Input(id='sample-size', type='number'),
    html.H4(children='Acceptance number'),
    dcc.Input(id='acceptance-number', type='number'),
    html.H4(children='LTPD error (%)'),
    dcc.Input(id='LTPD', type='number', value=10),
    ], style= {'float':'left', 'border': '1px solid black', 'padding': '10px','width':'auto', 'height':'500px'}),
    html.Div([
    dcc.Graph(id='graph')],  style={'float':'left', 'height':'700px'})
    ], style={'display':'table', 'clear':'both'})
app.scripts.config.serve_locally = True 


@app.callback(Output('graph', 'figure'),
              [Input('sample-size', 'value'), Input('acceptance-number', 'value'), Input('LTPD', 'value')]
              )
def plot_graph(n, c, LTPD):
    X=[i/10 for i in range(1000)]# initial x axis (percent defective)
    Y=[Pa(n,c,p)*100 for p in X]# initial y axis (probability of passing)
    # truncate the X axis
    i=0
    while Y[i]>LTPD:
        i+=1
    percMax=X[i]+1
    percArray=np.linspace(0,percMax, 100)
    perc=np.ndarray.tolist(percArray)
    prob=[Pa(n,c,p)*100 for p in perc]
    pdLTPD=(X[i]+X[i-1])/2 #the percent defective corresponding to LTPD
    traces = []
    Title='%(n)d samples, accept on %(c)d or fewer defects, %(pdLTPD).2f Percent defective at LTPD %(LTPD)d percent'% {'n':n, 'c':c, 'LTPD':LTPD, 'pdLTPD':pdLTPD}
    traces.append(go.Scatter(
        x=perc,
        y=prob,
        ))
    return {
        'data':traces,
        'layout': go.Layout(
        yaxis={'title': 'Probability of Passing'},
        xaxis={'title': 'Percent Defective'},
        title=Title,
        autosize=False,
        height=700,
        width=900,
        hovermode='closest',
        shapes=[{
                'type':'line',
                'x0':0,
                'x1':pdLTPD,
                'y0':LTPD,
                'y1':LTPD,
                'line':{
                'color':'rgb(256, 0, 0)'}
                },
                {
                'type':'line',
                'x0':pdLTPD,
                'x1':pdLTPD,
                'y0':0,
                'y1':LTPD,
                'line':{
                'color':'rgb(256,0,0)'}
                }
                ]
        )
        }
if __name__ == '__main__':
    app.run_server(debug=True)
