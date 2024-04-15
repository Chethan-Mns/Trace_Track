import ast
#import json
#import random
from typing import List
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
#from pathlib import Path
from fastapi.templating import Jinja2Templates
import pymongo
import certifi
from pydantic import BaseModel
import numpy as np
from bson import objectid
import osmnx as ox
import asyncio
from sse_starlette.sse import EventSourceResponse
ca = certifi.where()
client = pymongo.MongoClient(
    "mongodb+srv://sameer:x7SggQ1Jx1pk1K3D@mainproject.qjpme9r.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
db=client['main']
col=db['vehnav']
class Latlong(BaseModel):
    data:list
class LocationWithRouteId(BaseModel):
    data:list
    route_id:int
app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

app.mount("/static", StaticFiles(directory="src/static"), name="static")

route_with_coordinates={}

min_lat = 1000
max_lat = 0
min_log = 1000
max_log = 0
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = [ ]
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def boardcast_to_web(self,data):
        for conn in self.active_connections:
            try:
                await conn.send_json(data)
            except:
                self.disconnect(conn)
    async def boardcast_to_single(self,data,websocket:WebSocket):
        try:
            await websocket.send_json(data)
        except:
            self.disconnect(websocket)
manager=ConnectionManager()
class DemoRoute:
    def __init__(self,nodes):
        self.nodes=nodes
    def get_distance(self,index):
        target_point=self.given_coord
        if index>=len(self.nodes) or index<0:
            return False
        distance=ox.distance.great_circle_vec(target_point[1], target_point[0], self.nodes[index][1],self.nodes[index][0])
        print(distance)
        return distance
    def go_left(self,start_index,initial_dist):
        left_left_dis=self.get_distance(start_index-1)
        if not left_left_dis:
            return start_index
        if initial_dist<=left_left_dis:
            return start_index
        return self.go_left(start_index-1,left_left_dis)
    def go_right(self,start_index,initial_dist):
        right_right_dis=self.get_distance(start_index+1)
        if not right_right_dis:
            return start_index
        if initial_dist<=right_right_dis:
            return start_index
        return self.go_right(start_index+1,right_right_dis)
    def find_close_coord(self,given_coord,ref_index):
        self.given_coord=given_coord
        if ref_index >= len(self.nodes)-1:
            return len(self.nodes)-1
        if ref_index < 0:
            return 0
        if ref_index>0:
            left_index=ref_index-1
            right_index=ref_index+1
            ref_index_distance=self.get_distance(ref_index)
            right_index_distance=self.get_distance(right_index)
            left_index_distance=self.get_distance(left_index)
            if left_index_distance<ref_index_distance and left_index_distance<right_index_distance:
                return self.go_left(left_index,left_index_distance)
            elif right_index_distance<ref_index_distance and right_index_distance<left_index_distance:
                return self.go_right(right_index,right_index_distance)
            elif right_index_distance==left_index_distance and left_index_distance<ref_index_distance:
                left_low_index=self.go_left(left_index,left_index_distance)
                right_low_index=self.go_right(right_index,right_index_distance)
                if self.get_distance(left_low_index)<self.get_distance(right_low_index):
                    return left_low_index
                else:
                    return right_low_index
            else:
                return ref_index
        else:
            right_index = ref_index+1
            ref_index_distance = self.get_distance(ref_index)
            right_index_distance = self.get_distance(right_index)
            if right_index_distance < ref_index_distance:
                return self.go_right(right_index, right_index_distance)
            else:
                return ref_index

def calculate_min_max_values():
    global min_log,max_log,min_lat,max_lat
    for i in route_with_coordinates.keys():
        if min_lat > eval(i) [ 0 ]:
            min_lat = eval(i) [ 0 ]
        if max_lat < eval(i) [ 0 ]:
            max_lat = eval(i) [ 0 ]
        if min_log > eval(i) [ 1 ]:
            min_log = eval(i) [ 1 ]
        if max_log < eval(i) [ 1 ]:
            max_log = eval(i) [ 1 ]
        return True
def closestloc(lst, K):
    lst = np.asarray(lst)
    idx = (np.abs(lst-K)).argmin()
    return idx
# route 1 [[14.0215164, 80.031311], [14.050252, 79.9893781], [14.0599017, 79.9628101], [14.0713245, 79.9187454], [14.1014058, 79.8837577], [14.130623, 79.8654258], [14.1455181, 79.8533511]]
#route 2 [[14.039423182229296, 80.0175699846614], [14.147006983983504, 79.84839830836502], [14.149162305003554, 79.8466533567243], [14.154164798673163, 79.85076092142694], [14.155057526548937, 79.85350487513617], [14.15320303883741, 79.85359798974497]]
routes = {
    1: [ [ 14.0215164, 80.031311 ], [ 14.050252, 79.9893781 ], [ 14.061291, 79.962627 ], [ 14.0713245, 79.9187454 ],
         [ 14.1014058, 79.8837577 ], [ 14.130623, 79.8654258 ], [ 14.1455181, 79.8533511 ] ],
    2: [ [ 14.153609117216225, 79.8534321975779 ], [ 14.154512999426238, 79.8533790495253 ],
         [ 14.154462216784488, 79.85205335314478 ], [ 14.154195594417608, 79.85124026079106 ],
         [ 14.152948900548653, 79.84755436927567 ], [ 14.15040127853607, 79.84684673433213 ],
         [ 14.029955033861958, 80.02160004990253 ] ]}
#nodes=[[14.153191, 79.853600], [14.153214, 79.853506], [14.153203, 79.853381], [14.153036, 79.853333], [14.152980, 79.853308], [14.152464, 79.853232], [14.152212, 79.853202], [14.151778, 79.85311], [14.151279, 79.853078], [14.150762, 79.852956], [14.150327, 79.852934], [14.149993, 79.852906], [14.149504, 79.852911]]


@app.get("/index/{route_id}/")
async def index(request: Request, route_id: int):
    stages = [ {"label": "Stage"+str(x)} for x in range(1, len(routes [ int(route_id) ])+1) ]
    stages_with_start = [ {"label": "Start"} ]
    stages_with_start.extend(stages)
    return templates.TemplateResponse("spot.html", {"request": request, "totalpoints": len(routes [ int(route_id) ])+1,
                                                    "route_id": int(route_id), "admin": False,
                                                    "stages": stages_with_start, 'start_stage_index':
                                                        col.find_one({"route_cuurent_loc.route_id": int(route_id)},
                                                                     {"route_cuurent_loc.latest_loc.$": 1}) [
                                                            'route_cuurent_loc' ] [ 0 ] [ 'latest_loc' ]})


@app.get("/trackOnMap/{route_id}/")
async def trackOnMap(request: Request, route_id: int):
    return templates.TemplateResponse("trackOnMap.html", {"request": request, "stagesOfRoute": routes [ route_id ]})


@app.post('/addroute/')
async def addroute(latlong: Latlong):
    try:
        col.insert_one({"type": "route",
                        "mode": "testing2",
                        "codata": latlong.data})
        return {"status": True, "msg": f"{len(latlong.data)} Stages are recorded successfully,Thank You Sreeraj."}
    except Exception as e:
        return {"status": False,
                "msg": f"Error occured sreeraj in uploading data in mongodb contact sameer with this error {str(e)}"}
@app.get('/admin/post_loc/{route_id}/{passw}/')
async def update_bus_coordinates(request:Request,route_id,passw):
    if passw=="admin" and int(route_id) in [1,2]:
        stages = [ {"label": "Stage"+str(x)} for x in range(1, len(routes [ int(route_id) ])+1) ]
        stages_with_start = [ {"label": "Start"} ]
        stages_with_start.extend(stages)
        return templates.TemplateResponse("spot.html",
                                          {"request": request, "totalpoints":len(routes [ int(route_id) ])+1,"admin": True,"stages":stages_with_start,"route_id":int(route_id),'start_stage_index':col.find_one({"route_cuurent_loc.route_id":int(route_id)},{"route_cuurent_loc.latest_loc.$":1})['route_cuurent_loc'][0]['latest_loc']})
    else:
        return "password or route id are incorrect thank you"


STREAM_DELAY = 0.3 # second
RETRY_TIMEOUT=3000 #ms
@app.websocket('/EstablishCon/{route_id}/')
async def websocket_endpoint(websocket: WebSocket,route_id):
    await manager.connect(websocket)
    try:
        while(True):
            curr_loc = await websocket.receive_text()
            print(curr_loc)
            curr_loc = ast.literal_eval(curr_loc) [ 'data' ]
            if curr_loc == 'start':
                await manager.boardcast_to_single({"status": True, "id": "success"},websocket)
                continue
            Route = DemoRoute(routes [ int(route_id) ])
            latest_loc=col.find_one({"route_cuurent_loc.route_id": int(route_id)},{"route_cuurent_loc.latest_loc.$":1})
            loc_index = Route.find_close_coord(curr_loc,latest_loc['route_cuurent_loc'][0]['latest_loc']-1)
            print(routes [ int(route_id) ] [ loc_index ])
            if latest_loc['route_cuurent_loc'][0]['latest_loc']!=loc_index+1:
                col.update_one({"route_cuurent_loc.route_id": int(route_id)}, {
                "$set": {"route_cuurent_loc.$.latest_loc": loc_index+1, "route_cuurent_loc.$.update_status": True}})
            await manager.boardcast_to_single({'status': True, 'msg':"index Updated"},websocket)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(e.args)
        pass
@app.get('/stream/{route_id}/')
async def message_stream(request: Request,route_id):
    def new_messages():
        # Add logic here to check for new messages
        new_loc=col.find_one({"route_cuurent_loc.route_id":int(route_id)},{"route_cuurent_loc.update_status.$":1})
        return new_loc [ 'route_cuurent_loc' ] [ 0 ] [ 'update_status' ]
    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                print('break')
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                col.update_one({"route_cuurent_loc.route_id":int(route_id)},{"$set":{"route_cuurent_loc.$.update_status":False}})
                yield json.dumps({"event":"update",
                        "data":{"status":True,"loc_index":col.find_one({"route_cuurent_loc.route_id":int(route_id)},{"route_cuurent_loc.latest_loc.$":1})['route_cuurent_loc'][0]['latest_loc']}
                })

            await asyncio.sleep(STREAM_DELAY)
    return EventSourceResponse(event_generator(),headers={"Content-Type":"text/event-stream","Cache-Control":"no-cache","Connection": "keep-alive"},media_type="text/event-stream")
@app.post('/update_loc/')
async def update_loc(LWRI:LocationWithRouteId):
    Route=DemoRoute(routes[int(LWRI.route_id)])
    status,loc_index,msg=Route.find_close_coord(LWRI.data)
    col.update_one({"route_cuurent_loc.route_id":int(LWRI.route_id)},{"$set":{"route_cuurent_loc.$.latest_loc":loc_index+1,"route_cuurent_loc.$.update_status":True}})
    return {"status":True}