import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import sys

sys.path.append('src')
from pydantic import BaseModel
from controllers.vehicleToServer import VehicleToServer, VehicleToServerConnectionManager
from controllers.userToServer import userToServer
import ast
from errorHandling.errorHandlerWrapper import asyncWrapper

router = APIRouter(prefix="/vehicles",
                   tags=[ "vehicles" ])
connectionManager = VehicleToServerConnectionManager()
appController = userToServer()


class NewLocation(BaseModel):
    locationCoord: list
    busId: str


class DeviceIpAddress(BaseModel):
    ipAddress: str
    deviceId: str


@router.get("/getBusId/")
async def getBusId(request: Request):
    if "deviceId" in request.query_params:
        device = appController.getDevice(request.query_params [ "deviceId" ])
        return device


@router.post("/updateDeviceIpAddress/")
async def updateDeviceIpAddress(deviceIpaddress: DeviceIpAddress):
    updatedDevice = appController.modifyDevice(
        {"deviceId": deviceIpaddress.deviceId, "ipAddress": deviceIpaddress.ipAddress})
    return updatedDevice


@router.websocket('/EstablishConnectionWithServer/{deviceId}/')
async def websocket_endpoint(websocket: WebSocket, deviceId):
    busId = appController.getDevice(deviceId) [ 'allotedBusId' ]
    vehicleToServerController = VehicleToServer(busId)
    await connectionManager.connect(websocket, busId)
    appController.modifyBus({"busId": busId, "busRunningStatus": True})
    try:
        while True:
            msgFromVehicle = await websocket.receive_text()
            msgFromVehicle = ast.literal_eval(msgFromVehicle)
            if msgFromVehicle [ 'message' ] == 'connectionRequest':
                await connectionManager.boardcast_to_single(
                    {"busId": busId, "message": "Connection Established With Server"}, websocket)
                continue
            if msgFromVehicle [ 'message' ] == 'error occurred':
                appController.modifyBus({"busId": busId, "busRunningStatus": False})
                continue
            if await vehicleToServerController.updateBusNewLocation(msgFromVehicle):
                await connectionManager.boardcast_to_single(
                    {"busId": busId, "message": "Location Updated"}, websocket)
            else:
                await connectionManager.boardcast_to_single(
                    {"busId": busId, "message": "Location Not Updated"}, websocket)

    except WebSocketDisconnect:
        await connectionManager.disconnect(websocket, busId)
        appController.modifyBus({"busId": busId, "busRunningStatus": False})
    except Exception as e:
        print(e.args, 'erre')
        appController.modifyBus({"busId": busId, "busRunningStatus": False})
        pass
