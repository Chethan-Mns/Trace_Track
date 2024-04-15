import ast
import os

import jwt
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import sys

sys.path.append('src')
from errorHandling.customAPIsErrors import customApiError
from errorHandling.errorHandlerWrapper import asyncWrapper
from middleware.apiTokenValidations import token_required, get_current_user
from controllers.userToServer import userToServer
from typing import Optional
from utill.helperFunctions import getDateTime
from datetime import timedelta
from smtp.gmail_smtp import sentAccountVerificarionMail


class AddRouteType(BaseModel):
    allStages: list
    routeName: str
    routes: list
    areaName: str


class CurrentUser(BaseModel):
    userId: str

class SaveData(BaseModel):
    deviceId: Optional [ str ] = None
    busNumber: Optional [ str ] = None
    driverName: Optional [ str ] = None
    driverMobile: Optional [ str ] = None
    driverAddress: Optional [ str ] = None


router = APIRouter(prefix="/users",
                   tags=[ "users" ])
userToServerController = userToServer()


@router.post('/addroute/')
@asyncWrapper
async def addroute(routeDetails: AddRouteType, request: Request):
    return userToServerController.createRoute(routeDetails)


@router.get('/')
async def index():
    return


@router.post('/login/')
@asyncWrapper
async def login(request: Request):
    loginData = await request.json()
    checkUser = userToServerController.verifyUser(loginData [ 'email' ], loginData [ 'password' ])
    if checkUser [ 0 ]:
        if "rememberMe" in loginData and loginData [ "rememberMe" ] == "on":
            experyTime = getDateTime()+timedelta(days=7)
        else:
            experyTime = getDateTime()+timedelta(hours=12)
        token = jwt.encode({
            "userId": checkUser [ 1 ] [ 'userId' ],
            "exp": experyTime
        }, os.environ [ 'secret_key' ], algorithm='HS256')
        return {"userId": checkUser [ 1 ] [ 'userId' ], "token": token, "status": True,
                "message": "Successfully logged in",
                "rememberMe": "rememberMe" in loginData and loginData [ "rememberMe" ] == "on"}
    else:
        return {"status": False, "message": checkUser [ 1 ]}


@router.post('/register/')
async def register(request: Request):
    registerData = await request.json()
    print(registerData)
    checkUser = userToServerController.getUserByEmail(registerData [ 'email' ])
    print(checkUser)
    if checkUser:
        return {"status": False, "message": "User already exists"}
    newUser = userToServerController.createUser(registerData [ 'email' ], registerData [ 'password' ],
                                                registerData [ 'name' ])
    print(newUser)
    if newUser:
        verification = await sentAccountVerificarionMail(newUser [ 'username' ], newUser [ 'userId' ],
                                                         newUser [ 'name' ])
        print(verification)
    return {"status": True, "message": "User successfully registered"}


@router.get('/getFormStructure/')
async def getFormStructure(request: Request):
    if request.query_params.get('type') == 'driver':
        driverD = userToServerController.getDriverDataStructure()
        return {"driverDataStructure": driverD}
    elif request.query_params.get('type') == 'bus':
        busD = userToServerController.getVehicleDataStructure()
        return {"busDataStructure": busD}
    elif request.query_params.get('type') == 'device':
        deviceD = userToServerController.getDevicesDataStructure()
        return {"deviceDataStructure": deviceD}


@router.post('/saveData/')
async def saveData(request: Request, dataType: SaveData):
    if request.query_params.get('type') == 'driver':
        driver, driverId = userToServerController.createDriver(
            {"driverName": dataType.driverName, "driverAddress": dataType.driverAddress,
             "driverMobile": dataType.driverMobile})
        return {"savedData": driver, "id": driverId}
    elif request.query_params.get('type') == 'bus':
        bus, busId = userToServerController.createBus({"busNumber": dataType.busNumber})
        return {"savedData": bus, "id": busId}
    elif request.query_params.get('type') == 'device':
        device, deviceId = userToServerController.createDevice({"deviceId": dataType.deviceId})
        return {"savedData": device, "id": deviceId}
    return {"error": "Invalid request type"}


@router.get('/getData/')
async def getData(request: Request):
    if request.query_params.get('type') == 'driver':
        driver = userToServerController.getDriver(request.query_params.get('fid'))
        return driver
    elif request.query_params.get('type') == 'bus':
        bus = userToServerController.getBus(request.query_params.get('fid'))
        return bus
    elif request.query_params.get('type') == 'device':
        device = userToServerController.getDevice(request.query_params.get('fid'), )
        return device
    elif request.query_params.get('type') == 'route':
        route = userToServerController.getRouteDetails(request.query_params.get('fid'),
                                                       filterOut={"routeId": 1, "_id": 0, "routeName": 1, "areaName": 1,
                                                                  "allotedBusId": 1})
        return route
    return {"error": "Invalid request type"}


@router.get('/getNonAllotatedData/')
async def getNonAllotatedData(request: Request):
    if request.query_params.get('type') == 'driver':
        drivers = userToServerController.getAllDrivers(nonAllot=True,
                                                       filterOut={"_id": 0, "driverName": 1, "driverId": 1})
        return drivers
    elif request.query_params.get('type') == 'bus':
        bus = userToServerController.getAllBuses(nonAllot=True, checkFor=request.query_params.get('checkFor'),
                                                 filterOut={"_id": 0, "busNumber": 1, "busId": 1})
        return bus
    elif request.query_params [ 'type' ] == "device":
        devices = userToServerController.getAllDevices(nonAllot=True, filterOut={"_id": 0, "deviceId": 1})
        return devices
    elif request.query_params [ 'type' ] == "route":
        routes = userToServerController.getAllRoutes(nonAllot=True, filterOut={"_id": 0, "areaName": 1, "routeId": 1})
        return routes
    return {"error": "Invalid request type"}


@router.post("/updateData/")
async def updateData(request: Request):
    rUpdateData = await request.json()
    if request.query_params.get('type') == 'driver':
        driver = userToServerController.modifyDriver(rUpdateData)
        return {"updatedData": driver}
    elif request.query_params.get('type') == 'bus':
        bus = userToServerController.modifyBus(rUpdateData)
        return {"updatedData": bus}
    elif request.query_params.get('type') == 'device':
        device = userToServerController.modifyDevice(rUpdateData)
        return {"updatedData": device}
    elif request.query_params.get('type') == 'route':
        route = userToServerController.modifyRoute(rUpdateData)
        return {"updatedData": route}
    return {"error": "Invalid request type"}


@router.get("/deleteData/")
async def deleteData(request: Request):
    if request.query_params.get('type') == 'driver':
        driver = userToServerController.deleteDriver(request.query_params.get('dId'))
        return {"status": True}
    elif request.query_params.get('type') == 'route':
        route = userToServerController.deleteRoute(request.query_params.get('dId'))
        return {"status": True}
    elif request.query_params.get('type') == 'bus':
        bus = userToServerController.deleteBus(request.query_params.get('dId'))
        return {"status": True}
    elif request.query_params.get('type') == 'device':
        device = userToServerController.deleteDevice(request.query_params [ 'dId' ])
        return {"status": True}
    return {"status": False}


@router.get("/getRouteData/")
async def getRouteData(request: Request):
    busId = request.query_params.get('busId')
    bus = userToServerController.getBus(busId)
    routeId = bus [ 'allotedRouteId' ]
    routeData = userToServerController.getRouteDetails(routeId, {"routeStageWithNames": 1, "routeAllCoord": 1, "_id": 0,
                                                                 "allotedBusId": 1})
    return {"routeData": routeData}


@router.get('/locationStream/{busId}/')
async def locationStream(request: Request, busId, current_user: str = Depends(get_current_user)):
    return EventSourceResponse(userToServerController.eventGenerator(busId, request, current_user=current_user),
                               headers={"Cache-Control": "no-cache"})


@router.get('/locationStreamMultiple/')
async def locationStreamMultiple(request: Request, current_user: str = Depends(get_current_user)):
    busIds = ast.literal_eval(request.query_params.get('busIds'))

    return EventSourceResponse(
        userToServerController.eventGenerator(busIds, request, current_user=current_user, getType="multi"),
        headers={"Cache-Control": "no-cache"})
