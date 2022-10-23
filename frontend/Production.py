import io, base64, requests
import dash_bootstrap_components as dbc
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
df2 = pd.read_csv('traffic_his_sample.csv')

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


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
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
    
    html.Div([
        dcc.Graph(id='line_graph',
        style={'background-color':'rgb(205,221,233)', 'padding':'30px'})
    ]),
    
    dbc.Row(
        [
            dbc.Col(html.Div(
            [dcc.Upload( 
            id='upload-data', 
            children=html.Div([ 'Drag and Drop or ', 
            html.A('Select File') ], 
            style={
                'width': '96%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px' 
                }), 
            multiple=False
            )],

            style={'padding': '5px 10px',
                   'background-color': 'SkyBlue'}), width=6),

            dbc.Col(html.Div(id='upload-data-contents', 
            style={'marginLeft': 'auto', 'marginRight':'auto', 
                   'textAlign': 'center'}), 
            width=6)
        ],
        style={'background-color':'rgb(205,221,233)', 'padding':'30px'}
    ),
                    
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
    
    df_map = df.copy()
    df_map = df_map[df_map['CameraID'] == cam_id]
    geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in camera])

    if cam_id:
        cam = [dict(name = str(df_map.iloc[0,0]), lat = df_map.iloc[0,1], lon = df_map.iloc[0,2])]   
        geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in cam])

    new_map = dl.Map(
                children=[
                    dl.TileLayer(),
                    dl.GeoJSON(data=geojson, zoomToBounds=True)
                ],
                style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map")
    
    return new_map

# create line plot for past 30-min data
@app.callback(
    Output('line_graph', 'figure'), 
    Input('region_dd', 'value'),
    Input('camera_dd', 'value'))
def display_plot(reg, cam_id):
    ft1 = df2[df2.Region==reg]
    ft2 = ft1[ft1.Id==cam_id]
    fig = px.line(ft2, x='Time', y='Count',
                  title='Past 30 minutes')
    return fig

# copy from dash_app.py from dash_demo folder, only work for csv file
@app.callback(Output('upload-data-contents', 'children'),
             Input('upload-data', 'contents'))
def display_data(u_contents):
    if u_contents is not None:
        content_type, content_string = u_contents.split(',')

        decoded = base64.b64decode(content_string)
        in_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        in_dict = in_df.to_dict('list')
        print(in_dict)
        r1 = requests.post(url1, json=in_dict)
        in_df['predictions'] = pd.to_numeric(pd.Series(r1.json()))

        return dash_table.DataTable(
            in_df.to_dict('records'),
            [{'name': i, 'id': i} for i in in_df.columns],
            sort_action= 'native',
            filter_action='native', page_size=2,
            style_header={'background-color': 'DimGray',
                          'color':'white'},
            style_data_conditional=[
            {
            'if': {
                'column_id': 'predictions',
            },
            'backgroundColor': 'SandyBrown',
            'color': 'white'
            }]
        )

if __name__ == '__main__':
    app.run_server(debug=True)


