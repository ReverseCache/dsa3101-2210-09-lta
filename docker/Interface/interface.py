from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/traffic_speed")
async def traffic_speed():
    traffic_speed_df = requests.get(
        "http://fileservice:4321", traffic_speed_json)
    return traffic_speed_df


@app.get("/traffic_incidents")
async def traffic_speed():
    traffic_incidents_df = requests.get(
        "http://fileservice:4321", traffic_incidents_json)
    return traffic_incidents_df


@app.get("/new_weather")
async def traffic_speed():
    new_weather_df = requests.get("http://fileservice:4321", new_weather_json)
    return new_weather_df


class Image(BaseModel):
    msg: str


@app.post("/path")
async def function_demo_post(inp: Image):
    inp
    return {"message": "Sent"}
