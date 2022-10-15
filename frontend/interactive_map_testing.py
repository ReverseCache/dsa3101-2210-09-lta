import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, dcc, Output, Input
from dash_extensions.javascript import assign
import pandas as pd

##to put into dockerfile later
##pip install dash
##pip install dash-leaflet
##pip install dash-extensions
##pip install --upgrade protobuf==3.20.0

# A few cities 
cities = [dict(name="Orchard", lat=1.306440046857804, lon=103.83163997540888),
          dict(name="Ang Mo Kio", lat=1.3704522660724796, lon=103.84382793300924),
          dict(name="Punggol", lat=1.3983072367008103, lon=103.90840283165096)]

# get camera locations
df = pd.read_csv(r'C:\Users\Chermane Goh\OneDrive - National University of Singapore\Y3S1\git\dsa3101-2210-09-lta\model\camera_data\all_cameras_ids_locations.csv')
camera = []
for i in range(len(df)):
    d=dict(name = str(df.iloc[i,0]), lat = df.iloc[i,1], lon = df.iloc[i,2])
    camera.append(d)

# Create drop down options.
dd_options = [dict(value=c["name"], label=c["name"]) for c in camera]
dd_defaults = [o["value"] for o in dd_options]
# Generate geojson with a marker for each city and name as tooltip.
geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in camera])
# Create javascript function that filters on feature name.
geojson_filter = assign("function(feature, context){return context.props.hideout.includes(feature.properties.name);}")
# Create example app.
app = Dash()
app.layout = html.Div([
    
    dl.Map(
        children=[
        dl.TileLayer(),
        dl.GeoJSON(data=geojson, options=dict(filter=geojson_filter), hideout=dd_defaults, id="geojson", zoomToBounds=True)
        ],
        style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map"),
    
    html.Div(children=[
        html.Span("Select a region:"),
        dcc.Dropdown(
            id='title_dd',
            options=[{'label':'North', 'value':'North'},
                     {'label':'South', 'value':'South'},
                     {'label':'East', 'value':'East'},
                     {'label':'West', 'value':'West'}]),
    ]),

    html.Div(children=[
        html.Span("Select a camera id:"),
        dcc.Dropdown(id="dd", value=dd_defaults, options=dd_options, clearable=True),
    ]),
    
])

# Link drop down to geojson hideout prop (could be done with a normal callback, but clientside is more performant).
#app.clientside_callback("function(x){return x;}", Output("geojson", "hideout"), Input("dd", "value"))

@app.callback(
    Output("geojson", "hideout"),
    Input("dd", "value")
)
def update_output(value):
    return value

if __name__ == '__main__':
    app.run_server()




