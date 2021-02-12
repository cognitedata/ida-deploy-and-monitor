import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go
fig = go.Figure()

import os
from dotenv import load_dotenv
load_dotenv()
from cognite.client import CogniteClient

from markdown import markdown_text
import model
model.main()

client = CogniteClient(
    api_key = os.getenv("API_KEY"),
    project = "publicdata",
    client_name = "learn_module",
)

login_status = client.login.status()
user = login_status.user
project = login_status.project
logged_in = login_status.logged_in
text_output = f"The login status for {user} on {project} is {logged_in}."

app = dash.Dash(__name__)

app.layout = html.Div(children = [
    html.H1(children = [
        html.Div(id = "dashboard-title", children = "Pressure Forecast"),
        html.Div(
            id = "refresh-button-division", 
            children = html.Button(children = "Refresh", id = "refresh-button")
        ),
    ]),
    dcc.Tabs(
        id = "navigation_tabs",
        value = "Figures",
        children = [
            dcc.Tab(label = "Figures", value = "Figures"),
            dcc.Tab(label = "Statistics", value = "Statistics"),
            dcc.Tab(label = "Report", value = "Report"),
        ],
    ),
    html.Div(id = "tab_body"),
    html.Footer(children = [
        html.Div(f"user: {user}"),
        html.Div(f"project: {project}"),
        html.Div(
            id = "last-update-text",
            children = f"last update: {model.last_update}"
        ),
        ], 
        id = "global_footer",
    ),
    dcc.Interval(id = "interval-component", interval = 60*1000,),
    ],
)

@app.callback(
    Output("tab_body", "children"),
    [Input("navigation_tabs", "value")],
)
def render_tab(tab_label):
    if tab_label == "Figures":
        tab_body = html.Div(children = [
            dcc.Dropdown(
                id = "figure-selection",
                value = "Forecast",
                options = [
                    {"label": "Forecast", "value": "Forecast"},
                    {"label": "Historical", "value": "Historical"},
                    {"label": "Models", "value": "Models"},
                ],
            ),
            dcc.Graph(id = "graph-output", figure = fig),
        ])
    elif tab_label == "Statistics":
        tab_body = html.Div(children = html.Table(
            id = "stats-table",
            children = [
                html.Thead(html.Tr([html.Th(col) for col in model.df_statistics.columns])),
                html.Tbody([html.Tr([html.Td(model.df_statistics.iloc[i][col]) 
                for col in model.df_statistics.columns]) 
                for i in range(len(model.df_statistics))]),
            ]
        ))
    elif tab_label == "Report":
        tab_body = html.Div(children = dcc.Markdown(children = markdown_text))
    else:
        tab_body = html.Div(children = "UNKNOWN TAB")
    return tab_body

@app.callback(
    Output("graph-output", "figure"),
    Input("figure-selection", "value"),
    Input("refresh-button", "n_clicks"),
    Input("interval-component", "n_intervals"),
)
def render_figure(figure_name, clicks, interval):
    fig = go.Figure()

    if figure_name == "Forecast":
        fig.update_layout(title = "Forecast")
        fig.add_trace(go.Scatter(
            x = model.df_forecast["Timestamp"],
            y = model.df_forecast["Lin_Reg"],
            mode = "lines",
            name = "Linear Regression",
        ))
        fig.add_trace(go.Scatter(
            x = model.df_forecast["Timestamp"],
            y = model.df_forecast["Rnd_Forest"],
            mode = "lines",
            name = "Random Forest",
        ))
    elif figure_name == "Historical":
        fig.update_layout(title = "Historical")
        for name in model.ts_names:
            fig.add_trace(go.Scatter(
                x = model.df_historical.iloc[::10]["Timestamp"],
                y = model.df_historical.iloc[::10][name],
                name = name,
            ))
        fig.update_layout(legend_title_text = "Timeseries")
    elif figure_name == "Models":
        fig.update_layout(title = "Models")
        fig.add_trace(go.Scatter(
            x = model.df_historical.iloc[::10]["Timestamp"],
            y = model.df_historical.iloc[::10]["pi:160700"],
            mode = "markers",
            name = "pi:160700",
        ))
        fig.add_trace(go.Scatter(
            x = model.df_historical.iloc[::10]["Timestamp"],
            y = model.df_historical.iloc[::10]["Lin_Reg"],
            mode = "markers",
            name = "Linear Regression",
        ))
        fig.add_trace(go.Scatter(
            x = model.df_historical.iloc[::10]["Timestamp"],
            y = model.df_historical.iloc[::10]["Rnd_Forest"],
            mode = "markers",
            name = "Random Forest",
        ))
    else:
        fig.update_layout(title = "Unknown")
    return fig

@app.callback(
    Output("last-update-text", "children"), 
    Input("refresh-button", "n_clicks"),
    Input("interval-component", "n_intervals"),
)
def refresh_model(clicks, interval):
    model.main()
    return f"last update: {model.last_update}"


if __name__ == '__main__':
    app.run_server(debug=True)
