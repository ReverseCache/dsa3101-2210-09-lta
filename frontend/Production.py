import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, dcc, Output, Input
from dash_extensions.javascript import assign
import pandas as pd
import plotly.express as px

# get camera locations
##url = 'https://raw.githubusercontent.com/ReverseCache/dsa3101-2210-09-lta/main/frontend/traffic_image_region.csv?token=GHSAT0AAAAAABZPVYLWEQCR25P3XJOPIDYKY2UAHNQ'
##df = pd.read_csv(url, index_col=0)
df = pd.read_csv(r'C:\Users\Chermane Goh\OneDrive - National University of Singapore\Y3S1\git\dsa3101-2210-09-lta\frontend\traffic_count_sample.csv')

#scatter map plot showing count of cars across singapore
fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="Count", size="Count",
                        hover_name="CameraID", hover_data=["Region"],
                        color_continuous_scale=px.colors.sequential.Reds, size_max=15, zoom=10)
fig.update_layout(mapbox_style="open-street-map")


# interactive map displaying single camera
camera = []
for i in range(len(df)):
    d=dict(name = str(df.iloc[i,0]), lat = df.iloc[i,1], lon = df.iloc[i,2])
    camera.append(d)
# Create drop down options.
dd_options = [dict(value=c["name"], label=c["name"]) for c in camera]
dd_defaults = [o["value"] for o in dd_options]
# Generate geojson with a marker for each city and name as tooltip.
geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in camera])

region = list(df['Region'].unique())
cameraID = list(df['CameraID'].unique())

# create line plot
##line_fig = px.line(
##    ##df,
##    x='time',
##    y='count')

app = Dash()
app.layout = html.Div([

    html.Div(
        children=[
            html.H2('Current count of cars on the roads'),
            dcc.Graph(figure=fig,
                      style={'width': '80%', 'height': '100%', 'display':'inline-block'}),
        ],
        style={'text-align':'center', 'background-color':'#C9DEF5', 'padding':'30px'}
    ),
    
    html.Div(
        children=[
            html.H2('The following section will provide a breakdown of traffic situation at the camera location, please select the region and camera.'),
            html.Br(),
            html.H3('Select a Region'),
            dcc.Dropdown(
                id='region_dd',
                options=[{'label':r, 'value':r} for r in region],
                style={'width':'200px', 'margin':'0 auto'}),
            html.Br(),
            html.H3('Select a Camera'),
            dcc.Dropdown(
                id='camera_dd',
                optionHeight=30,
                maxHeight=150,
                style={'width':'200px', 'margin':'0 auto'}),
            html.Br(),
        ],
        
        style={'text-align':'center', 'vertical-align':'top', 'background-color':'rgb(205,221,233)', 'padding':'30px'}
    ),

    dl.Map(
        children=[
            dl.TileLayer(),
            dl.GeoJSON(data=geojson, id="geojson", zoomToBounds=True)
        ],
        style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map"),

    ##figure=line_plot
    html.Div([dcc.Graph(id='lineplot')])

])

# Create a callback from the Region dropdown to the CameraID Dropdown
@app.callback(
    Output('camera_dd', 'options'),
    Input('region_dd', 'value'))

def update_camera_dd(region_dd):
  
    region_camera = df[['Region', 'CameraID']].drop_duplicates()
    relevant_camera_options = region_camera[region_camera['Region'] == region_dd]['CameraID'].values.tolist()
    
    # Create and return formatted relevant options with the same label and value
    formatted_relevant_camera_options = [{'label':x, 'value':x} for x in relevant_camera_options]
    
    return formatted_relevant_camera_options

# Create a callback from the CameraID dropdown to the map
@app.callback(
    Output("map", "children"),
    Input("camera_dd", "value"))

def update_map(cam_id):
    
    map_title = 'All Cameras'
    df_map = df.copy()
    df_map = df_map[df_map['CameraID'] == cam_id]

    cam = [dict(name = str(df_map.iloc[0,0]), lat = df_map.iloc[0,1], lon = df_map.iloc[0,2])]   
    cam_geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in cam])

    new_map = dl.Map(
                children=[
                    dl.TileLayer(),
                    dl.GeoJSON(data=cam_geojson, zoomToBounds=True)
                ],
                style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map")
    
    return new_map

if __name__ == '__main__':
    app.run_server()




