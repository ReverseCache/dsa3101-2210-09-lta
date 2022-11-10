import torch
import io, base64, requests
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, dcc, Output, Input
from dash_extensions.javascript import assign
from PIL import Image
import pandas as pd
import plotly.express as px
import pika



main_df = pd.read_csv('main_df.csv')
incidents_df=pd.read_csv('traffic_incidents.csv')
df = pd.read_csv('traffic_count_sample.csv')
df2 = pd.read_csv('traffic_his_sample.csv')

#scatter map plot showing count of cars across singapore
fig = px.scatter_mapbox(main_df, lat="Latitude", lon="Longitude", color="Count", size="Count",
                        hover_data={'Latitude':False, 'Longitude': False, 'RoadName':True, 'Region':True, 'Count':True},
                        color_continuous_scale=px.colors.sequential.Reds, size_max=15, zoom=10)
fig.update_layout(mapbox_style="open-street-map")


# interactive map displaying single camera
camera = []
for i in range(len(main_df)):
    d=dict(name = main_df.iloc[i,6], lat = main_df.iloc[i,1], lon = main_df.iloc[i,2])
    camera.append(d)
# Create drop down options.
dd_options = [dict(value=c["name"], label=c["name"]) for c in camera]
dd_defaults = [o["value"] for o in dd_options]
# Generate geojson with a marker for each city and name as tooltip.
geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in camera])

region = list(main_df['Region'].unique())
cameraID = list(main_df['CameraID'].unique())
RoadName = list(main_df['RoadName'].unique())
cam_road=main_df[['CameraID', 'RoadName']].values.tolist()


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    
    html.Div(
        children=[
            dbc.Col(html.Img(src='https://www.lta.gov.sg/content/dam/ltagov/img/general/logo.png',style={'height': '60%','width':'60%'})),
            dbc.Col(html.H1('DSA3101 LTA 09')),
            dbc.Col(html.Img(src='https://i.ibb.co/4ZNhBgF/NUS-logo.png',style={'height': '80%','width':'70%'}))
        ],
        style= {'text-align':'center','display':'flex'}
    ),

    # map to show count of cars across Singapore
    html.Div(
        children=[
            html.H2('Real-time Count of Cars'),
            dcc.Graph(figure=fig,
                      style={'width': '80%', 'height': '100%', 'display':'inline-block'}),
        ]
    ),
    
    # Dropdown and map of selected camera
    html.Div(
        children=[
            html.H2('Real-time traffic situation'),
            html.Br(),
            html.Div([
                dbc.Col([
                    html.H4('Select a Region'),
                        dcc.Dropdown(
                        id='region_dd',
                        options=[{'label':r, 'value':r} for r in region],
                        style={'width':'300px', 'margin':'0 auto','text-align':'center'})]),
                dbc.Col([ 
                    html.H4('Select a Road'),
                    dcc.Dropdown(
                        id='camera_dd',
                        optionHeight=50,
                        maxHeight=150,
                        style={'width':'300px', 'margin':'0 auto','text-align':'center'})])
            ],
            style={'display':'flex'})
            ,
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
                    html.H4(id='rt_car_count'),
                    html.Br(),
                    html.H4(id='rt_jam'),
                    html.Br(),
                    html.H4(id='rainfall'),
                    html.Br(),
                    html.H4('Nearby Incidents:'),
                    html.H5(id='incidents'),
                    html.Br()]
            ),
            dbc.Col(html.Img(
                        id='traffic_image',
                        style={'height': '80%','width':'70%'}))
            
        ],
        style= {'text-align':'center','display':'flex'}
        ),

    # Historical data
    html.Div([
        html.H2('Historical Count of Cars'),
        dcc.Graph(id='line_graph',
                  style={'width': '90%', 'margin': 'auto'})
        ]),

    html.Br(),

    html.H2('Upload an image'),
    # Upload photo to view metrics, modified from dash_app.py (HDB demo)
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
            html.H4('Image Uploaded:'),
            html.Img(id='image',
                     style={'margin': '10px', 'height': '50%', 'width': '50%'}),
            html.Br(),
            html.Div([ 'Car count: ',
                html.H5(id='count') ]),
            html.Div([ 'Traffic jam: ',
                html.H5(id='tfjam') ])
            ])
                    
],
style={'text-align':'center', 'background-color':'#C9DEF5', 'padding':'30px'})



# Create a callback from the Region dropdown to the CameraID Dropdown
@app.callback(
    Output('camera_dd', 'options'),
    Input('region_dd', 'value'))

def update_camera_dd(region_dd):
  
    formatted_relevant_camera_options = [{'label':x[1], 'value':x[0]} for x in cam_road]
    if region_dd:
        region_camera = main_df[['Region', 'CameraID', 'RoadName']].drop_duplicates()
        relevant_camera_options = region_camera[region_camera['Region'] == region_dd][['CameraID', 'RoadName']].values.tolist()
    
        # Create and return formatted relevant options with the same label and value
        formatted_relevant_camera_options = [{'label':x[1], 'value':x[0]} for x in relevant_camera_options]
    
    return formatted_relevant_camera_options

# Create a callback from the CameraID dropdown to the map
@app.callback(
    Output("map", "children"),
    Input("camera_dd", "value"))

def update_map(cam_id):
    
    df_map = main_df.copy()
    df_map = df_map[df_map['CameraID'] == cam_id]
    geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['name'])} for c in camera])

    if cam_id:
        cam = [dict(name = df_map.iloc[0,0], lat = df_map.iloc[0,1], lon = df_map.iloc[0,2])]   
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
    if reg and cam_id:
        ft1 = df2[df2.Region==reg]
        # clear the road option to view all cameras within region
        if cam_id:
            ft1 = ft1[ft1.Id==cam_id]

    if reg:
        ft1 = df2[df2.Region==reg]

    if cam_id:
        ft1 = df2[df2.Id==cam_id]

    elif reg is None and cam_id is None:
        ft1 = df2
    fig = px.line(ft1, x='Time', y='Count', color='Id',
                  title='Past 30 minutes', markers=True)
    return fig

# display uploaded image
@app.callback(
    Output('image', 'src'),
    Input('upload-data', 'contents'))

def display_image(data):
    if data is not None:
        return data
    
# display metric from uploaded image
@app.callback(
    Output('count', 'children'),
    Output('tfjam', 'children'),
    Input('upload-data', 'filename'))

def display_metric(data):
    a=io.BytesIO()
    if data is not None:
        img = Image.open(data) #need to encode this image to string
        message = img.write(base64.b64encode(a.getvalue()).decode("utf-8"))

        global channel
        channel.basic_publish(exchange="", routing_key="ClientInterfaceQ",
            properties=pika.BasicProperties(headers={'key': 'ImagePrediction'}), body=message)
        
        #while loop to check ImagePrediction.csv available or not -> sleep if yes u display and destroy
        while
            try:
                pd.read_csv("Imageprediction.csv")
            except:
                time.sleep(5)
                
        # else:


        # count_vehicles, congested = get_metric()
        # return count1, tfjam1
    #     count_model = torch.hub.load('./yolov5', 'custom', path = './weights/count_best.pt', source='local')
    #     congestion_model = torch.hub.load('./yolov5', 'custom', path = './weights/congestion_best.pt', source='local')
    #     count_results = count_model(img)
    #     congestion_results = congestion_model(img)
    #     count_vehicles = list(map(len, count_results.pandas().xyxy))
    #     congestions = list(map(lambda x: min(sum(x["name"] == "congested"), 1), congestion_results.pandas().xyxy))
    #     if congestions[0]==1:
    #         congested="Yes"
    #     else:
    #         congested="No"
    #     return count_vehicles, congested
    # else:
    #     return None, None


# Create a callback from the CameraID dropdown to the traffic image
@app.callback(
    Output("traffic_image", "src"),
    Input("camera_dd", "value"))

def update_image(cam_id):

    link = 'https://i.ibb.co/k0Qty5c/no-camera-selected.png'
    traffic_image_url='http://datamall2.mytransport.sg/ltaodataservice/Traffic-Imagesv2'
    headers_val={'AccountKey':'AO4qMbK3S7CWKSlplQZqlA=='}
    if cam_id:
        traffic_image_req=requests.get(url=traffic_image_url,headers=headers_val)
        traffic_image_df=pd.DataFrame(eval(traffic_image_req.content)['value'])
        link = traffic_image_df.loc[traffic_image_df.CameraID == str(cam_id), 'ImageLink'].values[0]
    return link

# Create a callback from the CameraID dropdown to real time car count
@app.callback(
    Output("rt_car_count", "children"),
    Input("camera_dd", "value"))

def update_count(cam_id):
    count = 'please select a camera'
    if cam_id:
        count = main_df.loc[main_df.CameraID == cam_id, 'Count'].values[0]
    return f'Car count: {count}'

@app.callback(
    Output("rt_jam", "children"),
    Input("camera_dd", "value"))

def update_count(cam_id):
    jam = 'please select a camera'
    if cam_id:
        jam = main_df.loc[main_df.CameraID == cam_id, 'is_jam'].values[0]
        if jam == 1:
            jam="Yes"
        else:
            jam="No"
    return f'Jam : {jam}'

@app.callback(
    Output("rainfall", "children"),
    Input("camera_dd", "value"))

def update_rainfall(cam_id):
    rainfall = 'please select a camera'
    if cam_id:
        rainfall = main_df.loc[main_df.CameraID == cam_id, 'rainfall'].values[0]
    return f'Rainfall in mm: {rainfall}'

@app.callback(
    Output("incidents", "children"),
    Input("camera_dd", "value"))

def update_incidents(cam_id):
    incidents = 'please select a camera'
    incident_res=[]
    counter=1
    if cam_id:
        incident_res.append('%s incidents nearby, '%(len(incidents_df.loc[incidents_df['CameraID']==cam_id,].index)))
        incident_res.append(html.Br())
        for i in incidents_df.loc[incidents_df['CameraID']==cam_id,]['Message'].to_list():
            incident_res+= " %s. %s "%(counter,i)
            incident_res.append(html.Br())
            counter += 1
        incidents=incident_res
    return incidents


   

if __name__ == "__main__":
    # Connects ApiServer to RabbitMQ
    while True:
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters("rabbitmq", 5672, "/", credentials, heartbeat = 1000)
            )
            channel = connection.channel()
            break
        except Exception as e:
            print("ApiServer waiting for connection")
            time.sleep(5)


    # Receives message from ClientServer and sends it to ModelServer or FileServer
    channel.queue_declare(queue='ClientInterfaceQ')

    app.run_server(debug=True)