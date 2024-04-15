import json
import sys

sys.path.append('src')
from errorHandling.customAPIsErrors import customApiError
from models.vehiSpotDB import VehiSpotDb
import asyncio
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi import Request

from datetime import datetime, timedelta


class userToServer:

    def __init__(self):
        self.dbManager = VehiSpotDb()
        self.STREAM_DELAY = 0.2

    def getVehicleDataStructure(self):
        return [ "busNumber" ]

    def getDevicesDataStructure(self):
        return [ "deviceId" ]

    def getDriverDataStructure(self):
        return [ "driverName", "driverMobile", "driverAddress" ]

    def createUser(self, email, password, name):
        password = generate_password_hash(password)
        user = self.dbManager.createUser(
            {"username": email, "password": password, "name": str(name).capitalize(), "type": "student",
             "loginCount": 0, "favourite": "", "favouriteStage": ""})
        return user

    def getUserByUserId(self, userId):
        return self.dbManager.getUserByUserId(userId)

    def getUserByEmail(self, email):
        return self.dbManager.getUserByEmail(email)

    def activeAccount(self, userId):
        return self.dbManager.activateUser(userId)

    def verifyUser(self, email, password):
        user = self.dbManager.getUserByEmail(email)
        if user:
            if check_password_hash(user [ "password" ], password):
                if not user [ "active" ]:
                    return False, "User is not active"
                return True, user
            else:
                return False, "Incorrect Password"
        return False, "User Not Found"

    def createRoute(self, routeDetails):
        if not (routeDetails and routeDetails.allStages and routeDetails.routes):
            raise customApiError("Empty Stages or Route Data Not Found", 204)
        routeDetails.allStages = [ {"stageName": x [ 1 ], "stageCoord": x [ 0 ]} for x in routeDetails.allStages ]
        for i in range(len(routeDetails.routes [ 0 ] [ 'waypoints' ])): routeDetails.allStages [ i ] [
            'stageCoord' ] = [ routeDetails.routes [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lat' ],
                               routeDetails.routes [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lng' ] ]
        routeData = {
            "routeName": routeDetails.routeName,
            "routeStageWithNames": routeDetails.allStages,
            "routeAllCoord": routeDetails.routes [ 0 ] [ 'coordinates' ],
            "allotedBusId": "0",
            "totalRouteDistance": routeDetails.routes [ 0 ] [ 'summary' ] [ 'totalDistance' ],
            "routeMoreInfo": routeDetails.routes,
            "areaName": routeDetails.areaName,
            "busMoveDirection": "DOWN",
            "lastUpdatedLoc": [ ],
            "remarks": [ ],
            "routeStageVisitInfo": {},
            "curStage": 0,
        }
        r = self.dbManager.createRoute(routeData)
        route = {"Name": r [ 'areaName' ], "Sub Name": r [ 'routeName' ],
                 "Number of Stages": len(r [ 'routeStageWithNames' ]),
                 "Total Distance": r [ 'totalRouteDistance' ],
                 "Bus No": self.getBus(r [ 'allotedBusId' ]) [ "busNumber" ] if "allotedBusId" in r and r [
                     'allotedBusId' ] != "0" else 0}
        return route

    def createDriver(self, driverDetails):
        driverData = {
            "driverActiveStatus": True,
            "allotedBusId": "0"
        }
        driverData.update(driverDetails)
        d = self.dbManager.createDriver(driverData)
        driver = {"Name": d [ 'driverName' ], "Mobile": d [ 'driverMobile' ], "Address": d [ 'driverAddress' ],
                  "Bus No": self.getBus(d [ 'allotedBusId' ]) [ "busNumber" ] if "allotedBusId" in d and d [
                      'allotedBusId' ] != "0" else 0}
        return driver, d [ 'driverId' ]

    def modifyDriver(self, driverDetails):
        dbOut = self.dbManager.modifyDriver(driverDetails)
        return dbOut

    def deleteDriver(self, driverId):
        dbOut = self.dbManager.deleteDriver(driverId)
        return dbOut

    def getAllDrivers(self, nonAllot=False, filterOut={}):
        return self.dbManager.getAllDrivers(nonAllot, filterOut)

    def getDriver(self, driverId):
        return self.dbManager.getDriver(driverId)

    def createBus(self, busDetails):
        busData = {"busActiveStatus": True,
                   "busRunningStatus": False,
                   "allotedRouteId": "0",
                   "allotedDriverId": "0",
                   "allotedDeviceId": "0",
                   "totalStudentsOpt": 0
                   }
        busData.update(busDetails)
        b = self.dbManager.createVehicle(busData)
        bus = {"Number": b [ 'busNumber' ], "Driver Name": self.getDriver(b [ 'allotedDriverId' ]) [
            "driverName" ] if "allotedDriverId" in b and b [ 'allotedDriverId' ] != "0" else 0,
               "Route Name": self.getRouteDetails(b [ 'allotedRouteId' ]) [
                   "areaName" ] if "allotedRouteId" in b and b [ 'allotedRouteId' ] != "0" else 0,
               "Sub Route Name": self.getRouteDetails(b [ 'allotedRouteId' ]) [
                   "routeName" ] if "allotedRouteId" in b and b [ 'allotedRouteId' ] != "0" else 0,
               "Bus Running": b [ 'busRunningStatus' ],
               "Device Id": b [ 'allotedDeviceId' ] if "allotedDeviceId" in b else 0}

        return bus, b [ 'busId' ]

    def modifyBus(self, busDetails):
        dbOut = self.dbManager.modifyVehicle(busDetails)
        return dbOut

    def deleteBus(self, busId):
        dbOut = self.dbManager.deleteVehicle(busId)
        return dbOut

    def getAllBuses(self, nonAllot=False, filterOut={}, checkFor="Driver"):
        return self.dbManager.getAllVehicles(nonAllot, filterOut, checkFor=checkFor)

    def getBus(self, busId):
        return self.dbManager.getVehicle(busId)

    def createDevice(self, deviceDetails):
        deviceData = {"allotedBusId": "0", "ipAddress": "0",
                      "deviceMobileNumber": 0, "deviceActiveStatus": False}
        deviceData.update(deviceDetails)
        de = self.dbManager.createDevice(deviceData)
        device = {"Device Id": de [ 'deviceId' ],
                  "Bus No": self.getbus(de [ 'allotedBusId' ]) [ "busNumber" ] if "allotedBusId" in de and de [
                      'allotedBusId' ] != "0" else 0}
        return device, de [ 'deviceId' ]

    def modifyDevice(self, deviceDetails):
        dbOut = self.dbManager.modifyDevice(deviceDetails)
        return dbOut

    def getAllDevices(self, nonAllot=False, filterOut={}):
        return self.dbManager.getAllDevices(nonAllot, filterOut)

    def getDevice(self, deviceId):
        return self.dbManager.getDevice(deviceId)

    def deleteDevice(self, deviceId):
        return self.dbManager.deleteDevice(deviceId)

    def modifyRoute(self, routeDetails):
        if "routes" in routeDetails:
            routeDetails [ "routeAllCoord" ] = routeDetails [ 'routes' ] [ 0 ] [ 'coordinates' ]
            routeDetails [ "totalRouteDistance" ] = routeDetails [ 'routes' ] [ 0 ] [ 'summary' ] [ 'totalDistance' ]
            routeDetails [ "routeMoreInfo" ] = routeDetails [ 'routes' ]
            routeDetails [ 'allStages' ] = [ {"stageName": x [ 1 ], "stageCoord": x [ 0 ]} for x in
                                             routeDetails [ 'allStages' ] ]
            for i in range(len(routeDetails [ 'routes' ] [ 0 ] [ 'waypoints' ])): routeDetails [ 'allStages' ] [ i ] [
                'stageCoord' ] = [ routeDetails [ 'routes' ] [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lat' ],
                                   routeDetails [ 'routes' ] [ 0 ] [ 'waypoints' ] [ i ] [ 'latLng' ] [ 'lng' ] ]
            routeDetails [ "routeStageWithNames" ] = routeDetails [ 'allStages' ]
        dbOut = self.dbManager.modifyRoute(routeDetails)
        return dbOut

    def deleteRoute(self, routeId):
        dbOut = self.dbManager.deleteRoute(routeId)
        return dbOut

    def getRouteDetails(self, routeId, filterOut={}):
        routeData = self.dbManager.getRouteDetails(routeId, filterOut)
        return routeData

    def getAllRoutes(self, nonAllot=False, filterOut={}):
        AllRoutes = self.dbManager.getAllRoutes(nonAllot, filterOut)
        return AllRoutes

    def reformatD(self):
        reAllDrivers = self.dbManager.reformatDriversData()
        return reAllDrivers

    def reformatR(self):
        reAllRoutes = self.dbManager.reformatRoutesData()
        return reAllRoutes

    def reformatB(self):
        reAllBuses = self.dbManager.reformatBusesData()
        return reAllBuses

    def reformatDE(self):
        reAllDevices = self.dbManager.reformatDevicesData()
        return reAllDevices

    async def fetchLocation(self, busId):
        location = await self.dbManager.fetchRouteLocation(busId)
        return location

    async def eventGenerator(self, busId, request: Request, current_user, getType='single'):
        previous_data = None
        previous_data_multi = None
        self.dbManager.updateUserConnStatus(busId, current_user [ 'userId' ], True)
        while True:
            try:
                if await request.is_disconnected():
                    self.dbManager.updateUserConnStatus(busId, current_user [ 'userId' ], False)
                    print('break')
                    break
                if getType == 'multi':
                    latest_stage_data_multi = [
                        {"busId": bus, "stageDetails": await self.dbManager.getLatestStageDetails(bus)} for bus in
                        busId ]
                    if previous_data_multi is None:
                        previous_data_multi = [ None ] * len(latest_stage_data_multi)
                    if not all([ previous_data_multi [ i ] ==
                                 latest_stage_data_multi [ i ] [ 'stageDetails' ] [
                                     'location' ] for i in
                                 range(len(latest_stage_data_multi)) ]):
                        yield json.dumps(
                            {"event": "update", "stageDetailsMulti": latest_stage_data_multi})
                    previous_data_multi = [ d [ 'stageDetails' ] [ 'location' ] for d in latest_stage_data_multi ]
                    await asyncio.sleep(self.STREAM_DELAY)
                    continue
                latest_stage_data = await self.dbManager.getLatestStageDetails(busId)
                if previous_data != latest_stage_data [ 'location' ]:
                    yield json.dumps(
                        {"event": "update", "busId": busId, "moveDirection": latest_stage_data [ 'moveDirection' ],
                         "stageDetails": latest_stage_data,
                         "location": latest_stage_data [ 'location' ], "speed": latest_stage_data [ 'speed' ]})
                    previous_data = latest_stage_data [ 'location' ]
                await asyncio.sleep(self.STREAM_DELAY)
            except Exception as e:
                print(f"Error occurred: {e}")
