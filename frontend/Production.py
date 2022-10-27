import io, base64, requests
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, dcc, Output, Input
from dash_extensions.javascript import assign
import pandas as pd
import plotly.express as px\



# get camera locations
##url = 'https://raw.githubusercontent.com/ReverseCache/dsa3101-2210-09-lta/main/frontend/traffic_image_region.csv?token=GHSAT0AAAAAABZPVYLWEQCR25P3XJOPIDYKY2UAHNQ'
##df = pd.read_csv(url, index_col=0)
df = pd.read_csv('traffic_count_sample.csv')
df2 = pd.read_csv('traffic_his_sample.csv')

#scatter map plot showing count of cars across singapore
fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color="Count", size="Count",
                        hover_data={'Latitude':False, 'Longitude': False, 'CameraID':True, 'Region':True, 'Count':True},
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
            dbc.Col(html.Img(src='https://www.lta.gov.sg/content/dam/ltagov/img/general/logo.png',style={'height': '60%','width':'60%'})),
            dbc.Col(html.H1('DSA3101 LTA 09')),
            dbc.Col(html.Img(src='https://raw.githubusercontent.com/ReverseCache/dsa3101-2210-09-lta/main/frontend/NUS_logo.png?token=GHSAT0AAAAAABZPVZKPEHPIWLNDGK2AQ6XGY22NJSA',style={'height': '80%','width':'70%'}))
        ],
        style= {'text-align':'center','display':'flex'}
    ),

    # map to show count of cars across Singapore
    html.Div(
        children=[
            html.H2('Current count of cars on the roads'),
            dcc.Graph(figure=fig,
                      style={'width': '80%', 'height': '100%', 'display':'inline-block'}),
        ]
    ),
    
    # Dropdown and map of selected camera
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
        
        style={'text-align':'center', 'vertical-align':'top', 'padding':'30px'}
    ),
    dl.Map(
        children=[
            dl.TileLayer(),
            dl.GeoJSON(data=geojson, id="geojson", zoomToBounds=True)
        ],
        style={'width': '80%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map"
        ),

    html.Br(),

    html.Div(
        children=[
            dbc.Col([
                    html.H4(id='car count'),
                    html.Br(),
                    html.H4('Rainfall:'+'<RAINFALL at nearest weather station>'),
                    html.Br(),
                    html.H4('Nearby Incidents:'+'<NEAREST INCIDENT>'),
                    html.Br()]
            ),
            dbc.Col(html.Img(
                        id='traffic image',
                        style={'height': '80%','width':'70%'}))
            
        ],
        style= {'text-align':'center','display':'flex'}
        ),

    # Historical data
    html.Div([
        dcc.Graph(id='line_graph',
                  style={'width': '90%', 'margin': 'auto'})
        ]),

    html.Br(),

    html.H2('Upload a image'),
    # Upload photo to view metrics
    html.Div([
        dcc.Upload( 
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
            'margin': '10px',
            'background-color': 'SkyBlue'
            }), 
        multiple=False,
        style={'width': '60%', 'margin': 'auto'}
        )]
    ),
    
    html.Br(),
    
    html.Div([
            html.H5('Image Uploaded:'),
            html.Img(id='upload-data-contents',
                     style={'margin': '10px', 'height': '50%', 'width': '50%'}),
            html.Br(),
            #html.Img(src='https://i.imgur.com/kqLjRl7.jpg',style={'height': '50%','width':'40%'}),
            html.Div([ 'Car count: ' + '<UPLOADED COUNT> ' + 'eg, ',
                html.A(id='count') ])
            ])
                    
],
style={'text-align':'center', 'background-color':'#C9DEF5', 'padding':'30px'})



# Create a callback from the Region dropdown to the CameraID Dropdown
@app.callback(
    Output('camera_dd', 'options'),
    Input('region_dd', 'value'))

def update_camera_dd(region_dd):
  
    formatted_relevant_camera_options = [{'label':x, 'value':x} for x in cameraID]
    if region_dd:
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
    fig = px.line(ft2, x='Time', y='Count', title='Past 30 minutes')
    return fig

# display uploaded image
@app.callback(
    Output('upload-data-contents', 'src'),
    Input('upload-data', 'contents'))

def display_image(u_contents):
    if u_contents is not None:
        return u_contents
    
# copy from dash_app.py, need to modify
@app.callback(
    Output('count', 'children'),
    Input('upload-data', 'contents'))

def display_metric(u_contents):
    if u_contents is not None:
        #content_type, content_string = u_contents.split(',')

        #decoded = base64.b64decode(content_string)
        #in_df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        #in_dict = in_df.to_dict('list')
        #print(in_dict)
        #r1 = requests.post(url1, json=in_dict)
        #in_df['predictions'] = pd.to_numeric(pd.Series(r1.json()))

        wt=df.Count[0] # replace with predicted image metric
        return wt

# Create a callback from the CameraID dropdown to the traffic image
@app.callback(
    Output("traffic image", "src"),
    Input("camera_dd", "value"))

def update_image(cam_id):

    link = 'https://raw.githubusercontent.com/ReverseCache/dsa3101-2210-09-lta/main/frontend/no_camera_selected.png?token=GHSAT0AAAAAABZPVZKOO5GD6M7K53VBAFN6Y22NCIQ'
    traffic_image_url='http://datamall2.mytransport.sg/ltaodataservice/Traffic-Imagesv2'
    headers_val={'AccountKey':'AO4qMbK3S7CWKSlplQZqlA=='}
    
    if cam_id:
        traffic_image_req=requests.get(url=traffic_image_url,headers=headers_val)
        traffic_image_df=pd.DataFrame(eval(traffic_image_req.content)['value'])
        #link = traffic_image_df[traffic_image_df['CameraID'] == cam_id]
        #link = link.iloc[0,3]
        link = traffic_image_df.loc[traffic_image_df.CameraID == str(cam_id), 'ImageLink'].values[0]

    return link

# Create a callback from the CameraID dropdown to count
@app.callback(
    Output("car count", "children"),
    Input("camera_dd", "value"))

def update_count(cam_id):
    count = 'please select a camera'
    if cam_id:
        count = df.loc[df.CameraID == cam_id, 'Count'].values[0]
    return f'Car count: {count}'


if __name__ == '__main__':
    app.run_server(debug=True)


