from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import os
import base64

from app import app
from apps.data import df_3



token = open(".mapbox_token").read() 

layout = dbc.Container([
        dbc.Container([
            dbc.Row([
                dbc.Col([html.P("Select Pizza Style:   ", className = "p-metric-title"),
                        dbc.RadioItems(id = "pizza-style-radio",
                                        options = [{"label": "Plain", "value": "Plain"},
                                                    {"label": "Other", "value": "Other"}],
                                        value = "Plain",
                                        inline = True,
                                        labelClassName = "radio-button-label",
                                        labelCheckedClassName = "radio-button-checked")], className = "col-center")
                ])
            ],  className = "container-box-radio"),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id = "map-graph", 
                                config = {"displayModeBar": False}, 
                                clear_on_unhover=True), 
                    dcc.Tooltip(id = "graph-tooltip", style = {"background-color": "#181b1b"})
                ], className = "col-center")
            ])
        ], className = "container-box")
    ])




@app.callback([Output("map-graph", "figure"),
                Output("graph-tooltip", "show"),
                Output("graph-tooltip", "children"),
                Output("graph-tooltip", "bbox")],
                [Input("pizza-style-radio", "value"),
                Input("map-graph", "hoverData")])

def create_layout(pizza_style,hover):

    df_plot = df_3.loc[(df_3["Style_Renamed"] == pizza_style)].sort_values(by = "Price as number").copy()

    fig = go.Figure()

    for size in df_plot["Price size"].unique():
        price_range = df_plot.loc[df_plot["Price size"] == size, "Price range"].unique()[0]
        df_plot_2 = df_plot.loc[df_plot["Price size"] == size].copy()
        fig.add_trace(go.Scattermapbox(lat = df_plot_2["location_lat"], lon= df_plot_2["location_lng"],
                                        marker = dict(color = df_plot["Colour"].iloc[0], size = size, opacity = 0.7),
                                        customdata= df_plot_2[["Name", "Price as number"]],
                                        hovertemplate = None,
                                        hoverinfo = "none",
                                        name = price_range,
                                        ))



    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token,
                    mapbox_zoom=12, mapbox_center = {"lat": 40.728175, "lon": -73.985147},
                    margin={"r":0,"t":0,"l":0,"b":0},
                    showlegend = True,
                    legend = dict(title= "Price Range", bgcolor = "#181b1b", font = dict(color = "#ECF0F1"), itemsizing = "trace"),
                    plot_bgcolor = "#181b1b",
                    paper_bgcolor = "#181b1b",
                    height = 540,
                    width = 840
                    )
    
    if hover is None:
        return fig, False, None, None

    
    

    hover_name = hover["points"][0]["customdata"][0]
    hover_image = df_plot.loc[df_plot["Name"] == hover_name, "Image Name"].iloc[0]
    hover_image = "assets/images/{}".format(hover_image)
    image_filename = os.path.join(os.getcwd(), hover_image) 
    test_base64 = base64.b64encode(open(image_filename, 'rb').read()).decode('ascii')

    hover_price = df_plot.loc[df_plot["Name"] == hover_name, "Price as number"].iloc[0]

    if pizza_style == "Plain":
        COLOUR = "#D4AC0D"
    else:
        COLOUR = "#BA4A00"

    children = [
        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(test_base64)),
            html.H2("{}".format(hover_name), style = {"font-size": 22, "color": COLOUR}),
            html.P("Price: ${:.2f}".format(hover_price), style = {"font-size": 16, "color": COLOUR, "margin-left": 0}),
        ])
    ]

    bbox = hover["points"][0]["bbox"]

    return fig, True, children, bbox



   #sort out hover template with images
   #sort the legend out so when it clisk then it filters the ones just clicked







