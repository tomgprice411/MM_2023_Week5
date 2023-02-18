from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import os
import base64

from app import app
from apps.data import df_3


# assign the mapbox token so we can create map graph from mapbox
#Note: I have a hidden file called '.mapbox_token' which contains my specific token from MapBox. To get the MapBox toek you need to create an account and geenrate a public token
# token = open(".mapbox_token").read() 
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']

#now create the layout structure (this is what the app calls from index.py)
layout = dbc.Container([
        dbc.Container([
            dbc.Row([
                dbc.Col([html.P("Select Pizza Style:   ", className = "p-metric-title"),
                        #create a radio button to select whether you the user wants to see plain pizzas or other types of pizza
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
                    #create the placeholder for the graph, the actual map graph is created in the below callback function
                    dcc.Graph(id = "map-graph", 
                                config = {"displayModeBar": False}, 
                                clear_on_unhover=True), 
                    dcc.Tooltip(id = "graph-tooltip", style = {"background-color": "#181b1b"})
                ], className = "col-center")
            ])
        ], className = "container-box")
    ])



#create the callback
#this is used to make the graph interactive
#pass the results from the radio button as well as what pizza parlour the user is hovering over, so tthe dashboard can be updated with these
@app.callback([Output("map-graph", "figure"),
                Output("graph-tooltip", "show"),
                Output("graph-tooltip", "children"),
                Output("graph-tooltip", "bbox")],
                [Input("pizza-style-radio", "value"),
                Input("map-graph", "hoverData")])

# the function creates the visuals that will be passed to the layout structure above
def create_layout(pizza_style,hover):

    #filter the dataframe so it only contains the style of pizza that's been selected from the radio button
    df_plot = df_3.loc[(df_3["Style_Renamed"] == pizza_style)].sort_values(by = "Price as number").copy()

    #create a blank plotyl canvas
    fig = go.Figure()

    #loop over each of the 4 price ranges to create 4 separate maps overlayed on top of each other
    #this was done to create the legend that labels each sized bubble with what price range it corresponds to
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


    #customise the map
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
    
    #if the user isn't hovering over a data point then only return the graph and nothing else
    #the dashboard will break without this
    if hover is None:
        return fig, False, None, None

    
    #get the pizza parlour name, price and image that the user is hover over
    #this is to feed into the tooltip that will appear
    hover_name = hover["points"][0]["customdata"][0]
    hover_price = df_plot.loc[df_plot["Name"] == hover_name, "Price as number"].iloc[0]
    hover_image = df_plot.loc[df_plot["Name"] == hover_name, "Image Name"].iloc[0]
    hover_image = "assets/images/{}".format(hover_image)
    image_filename = os.path.join(os.getcwd(), hover_image) 

    #encode and decode the image, otherwise the image won't load in the tooltip
    test_base64 = base64.b64encode(open(image_filename, 'rb').read()).decode('ascii')

    
    #personalise the colour of the tooltip depending on what pizza style is selected
    if pizza_style == "Plain":
        COLOUR = "#D4AC0D"
    else:
        COLOUR = "#BA4A00"

    #create the layout of the tooltip
    children = [
        html.Div([
            html.Img(src='data:image/png;base64,{}'.format(test_base64)),
            html.H2("{}".format(hover_name), style = {"font-size": 22, "color": COLOUR}),
            html.P("Price: ${:.2f}".format(hover_price), style = {"font-size": 16, "color": COLOUR, "margin-left": 0}),
        ])
    ]

    bbox = hover["points"][0]["bbox"]

    return fig, True, children, bbox



