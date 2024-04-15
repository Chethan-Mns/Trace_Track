import json
import sys

sys.path.append('src')
from config.dbConfig import db
from bson import json_util
from utill.helperFunctions import getCurrentTime, getUniqueId, getCurrentDateForDb


class VehiSpotDb:

    def __init__(self):
        self.routesCol = db [ 'routes' ]
        self.usersCol = db [ 'users' ]
        self.vehiclesCol = db [ 'vehicles' ]
        self.driversCol = db [ 'drivers' ]
        self.devicesCol = db [ 'devices' ]

    def createRoute(self, routeData):
        routeData [ "routeId" ] = getUniqueId()
        routeData [ "createdAt" ] = getCurrentTime()
        routeData [ "updatedAt" ] = getCurrentTime()
        self.routesCol.insert_one(routeData)
        return json.loads(json_util.dumps(routeData))

    def modifyRoute(self, routeData, insideCal=False):
        routeData [ "updatedAt" ] = getCurrentTime()
        oldData = self.routesCol.find_one({"routeId": routeData [ "routeId" ]})
        if "allotedBusId" in routeData and not insideCal:
            self.modifyVehicle({"allotedRouteId": routeData [ "routeId" ], "busId": routeData [ 'allotedBusId' ]},
                               insideCal=True)
            if oldData [ "allotedBusId" ] != routeData [ "allotedBusId" ] and oldData [ "allotedBusId" ] != '0':
                self.modifyVehicle({"allotedRouteId": "0", "busId": oldData [ "allotedBusId" ]}, insideCal=True)
        self.routesCol.update_one({"routeId": routeData [ "routeId" ]}, {"$set": routeData})
        return json.loads(json_util.dumps(routeData))

    def deleteRoute(self, routeId):
        self.vehiclesCol.update_one({"allotedRouteId": routeId}, {"$set": {"allotedRouteId": "0"}})
        self.routesCol.delete_one({"routeId": routeId})
        return routeId

    def createUser(self, userData):
        userData [ "createdAt" ] = getCurrentTime()
        userData [ "updatedAt" ] = getCurrentTime()
        userData [ "userId" ] = getUniqueId()
        userData [ "active" ] = False
        self.usersCol.insert_one(userData)
        return json.loads(json_util.dumps(userData))

    def getUserByUserId(self, userId):
        return json.loads(json_util.dumps(self.usersCol.find_one({"userId": userId})))

    def getUserByEmail(self, email):
        return json.loads(json_util.dumps(self.usersCol.find_one({"username": email})))

    def activateUser(self, userId):
        user = self.getUserByUserId(userId)
        if user [ "active" ]:
            return False, True, "Already activated"
        if not user:
            return False, False, "Invalid Link"
        self.usersCol.update_one({"userId": userId}, {"$set": {"active": True}})
        return True, True, "User activated"

    def createVehicle(self, vehicleData):
        vehicleData [ 'busNumber' ] = vehicleData [ 'busNumber' ].upper()
        vehicleData [ "busId" ] = getUniqueId()
        vehicleData [ "createdAt" ] = getCurrentTime()
        vehicleData [ "updatedAt" ] = getCurrentTime()
        self.vehiclesCol.insert_one(vehicleData)
        return json.loads(json_util.dumps(vehicleData))

    def modifyVehicle(self, vehicleData, insideCal=False):
        print(vehicleData)
        vehicleData [ "updatedAt" ] = getCurrentTime()
        oldData = self.vehiclesCol.find_one({"busId": vehicleData [ "busId" ]})
        print(oldData)
        if "allotedDriverId" in vehicleData and not insideCal:
            self.modifyDriver({"allotedBusId": vehicleData [ "busId" ], "driverId": vehicleData [ "allotedDriverId" ]},
                              insideCal=True)
            if oldData [ "allotedDriverId" ] != vehicleData [ "allotedDriverId" ] and oldData [
                "allotedDriverId" ] != '0':
                self.modifyDriver({"allotedBusId": "0", "driverId": oldData [ "allotedDriverId" ]}, insideCal=True)
        if "allotedDeviceId" in vehicleData and not insideCal:
            self.modifyDevice({"allotedBusId": vehicleData [ "busId" ], "deviceId": vehicleData [ 'allotedDeviceId' ]},
                              insideCal=True)
            if oldData [ "allotedDeviceId" ] != vehicleData [ "allotedDeviceId" ] and oldData [
                "allotedDeviceId" ] != '0':
                self.modifyDevice({"allotedBusId": "0", "deviceId": oldData [ "allotedDeviceId" ]}, insideCal=True)
        if "allotedRouteId" in vehicleData and not insideCal:
            self.modifyRoute({"allotedBusId": vehicleData [ "busId" ], "routeId": vehicleData [ "allotedRouteId" ]},
                             insideCal=True)
            if oldData [ "allotedRouteId" ] != vehicleData [ "allotedRouteId" ] and oldData [ "allotedRouteId" ] != '0':
                self.modifyRoute({"allotedBusId": "0", "routeId": oldData [ "allotedRouteId" ]}, insideCal=True)

        self.vehiclesCol.update_one({"busId": vehicleData [ "busId" ]}, {"$set": vehicleData})
        return json.loads(json_util.dumps(vehicleData))

    def deleteVehicle(self, busId):
        self.driversCol.update_one({"allotedBusId": busId}, {"$set": {"allotedBusId": "0"}})
        self.devicesCol.update_one({"allotedBusId": busId}, {"$set": {"allotedBusId": "0"}})
        self.routesCol.update_one({"allotedBusId": busId}, {"$set": {"allotedBusId": "0"}})
        self.vehiclesCol.delete_one({"busId": busId})
        return busId

    def getAllVehicles(self, nonAllot, filterOut, checkFor='Driver'):
        if nonAllot:
            allVehicles = self.vehiclesCol.find({f"alloted{checkFor}Id": "0"}, filterOut)
        else:
            allVehicles = self.vehiclesCol.find({}, filterOut)
        return json.loads(json_util.dumps(allVehicles))

    def getVehicle(self, busId):
        return json.loads(json_util.dumps(self.vehiclesCol.find_one({"busId": busId}, {"_id": 0, "allotedRouteId": 1,
                                                                                       "allotedDriverId": 1,
                                                                                       "allotedDeviceId": 1,
                                                                                       "busNumber": 1, "busId": 1})))

    def createDriver(self, driverData):
        driverData [ "updatedAt" ] = getCurrentTime()
        driverData [ "createdAt" ] = getCurrentTime()
        driverData [ "driverId" ] = getUniqueId()
        self.driversCol.insert_one(driverData)
        return json.loads(json_util.dumps(driverData))

    def modifyDriver(self, driverData, insideCal=False):
        driverData [ "updatedAt" ] = getCurrentTime()
        oldData = self.driversCol.find_one({"driverId": driverData [ "driverId" ]})
        if 'allotedBusId' in driverData and not insideCal:
            self.modifyVehicle({"allotedDriverId": driverData [ 'driverId' ], "busId": driverData [ "allotedBusId" ]},
                               insideCal=True)
            if oldData [ "allotedBusId" ] != driverData [ "allotedBusId" ] and oldData [ "allotedBusId" ] != '0':
                self.modifyVehicle({"allotedDriverId": "0", "busId": oldData [ "allotedBusId" ]}, insideCal=True)
        self.driversCol.update_one({"driverId": driverData [ "driverId" ]}, {"$set": driverData})
        return json.loads(json_util.dumps(driverData))

    def deleteDriver(self, driverId):
        self.vehiclesCol.update_one({"allotedDriverId": driverId}, {"$set": {"allotedDriverId": "0"}})
        self.driversCol.delete_one({"driverId": driverId})
        return driverId

    def getAllDrivers(self, nonAllot, filterOut):
        if nonAllot:
            allDrivers = self.driversCol.find({"allotedBusId": "0"}, filterOut)
        else:
            allDrivers = self.driversCol.find({}, filterOut)
        return json.loads(json_util.dumps(allDrivers))

    def getDriver(self, driverId):
        return json.loads(json_util.dumps(self.driversCol.find_one({"driverId": driverId},
                                                                   {"_id": 0, "allotedBusId": 1, "driverName": 1,
                                                                    "driverAddress": 1, "driverMobile": 1,
                                                                    "driverId": 1, })))

    def createDevice(self, deviceData):
        deviceData [ "updatedAt" ] = getCurrentTime()
        deviceData [ "createdAt" ] = getCurrentTime()
        self.devicesCol.insert_one(deviceData)
        return json.loads(json_util.dumps(deviceData))

    def modifyDevice(self, deviceData, insideCal=False):
        deviceData [ "updatedAt" ] = getCurrentTime()
        oldData = self.devicesCol.find_one({"deviceId": deviceData [ "deviceId" ]})
        if "allotedBusId" in deviceData and not insideCal:
            self.modifyVehicle({"allotedDeviceId": deviceData [ "deviceId" ], "busId": deviceData [ "allotedBusId" ]},
                               insideCal=True)
            if oldData [ "allotedBusId" ] != deviceData [ "allotedBusId" ] and oldData [ "allotedBusId" ] != '0':
                self.modifyVehicle({"allotedDeviceId": "0", "busId": oldData [ "allotedBusId" ]}, insideCal=True)
        self.devicesCol.update_one({"deviceId": deviceData [ "deviceId" ]}, {"$set": deviceData})
        return json.loads(json_util.dumps(deviceData))

    def deleteDevice(self, deviceId):
        self.vehiclesCol.update_one({"allotedDeviceId": deviceId}, {"$set": {"allotedDeviceId": "0"}})
        self.devicesCol.delete_one({"deviceId": deviceId})
        return deviceId

    def getAllDevices(self, nonAllot, filterOut):
        if nonAllot:
            allDevices = self.devicesCol.find({"allotedBusId": "0"}, filterOut)
        else:
            allDevices = self.devicesCol.find({}, filterOut)
        return json.loads(json_util.dumps(allDevices))

    def getDevice(self, deviceId):
        return json.loads(json_util.dumps(
            self.devicesCol.find_one({"deviceId": deviceId},
                                     {"_id": 0, "allotedBusId": 1, "deviceId": 1, "ipAddress": 1})))

    def getRouteDetails(self, routeId, filterOut):
        routeData = self.routesCol.find_one({"routeId": routeId}, filterOut)
        return json.loads(json_util.dumps(routeData))

    def getAllRoutes(self, nonAllot, filterOut):
        if nonAllot:
            allRoutes = self.routesCol.find({"allotedBusId": "0"}, filterOut)
        else:
            allRoutes = self.routesCol.find({}, filterOut)
        return json.loads(json_util.dumps(allRoutes))

    def reformatBusesData(self):
        # Define the pipeline for the aggregation
        pipeline = [
            {
                '$lookup': {
                    'from': 'drivers',  # collection to join
                    'localField': 'allotedDriverId',  # field from the first table
                    'foreignField': 'driverId',  # field from the second table
                    'as': 'driverData'  # alias for the joined data
                }
            },
            {
                '$unwind': {
                    "path": "$driverData",
                    "preserveNullAndEmptyArrays": True
                }  # deconstruct the array field
            },
            {
                '$lookup': {
                    'from': 'routes',  # collection to join
                    'localField': 'allotedRouteId',  # field from the joined data
                    'foreignField': 'routeId',  # field from the third table
                    'as': 'routeData'  # alias for the joined data
                }
            },
            {
                '$unwind': {
                    "path": "$routeData",
                    "preserveNullAndEmptyArrays": True
                }  # deconstruct the array field
            },
            {
                '$project': {
                    '_id': 0,
                    'busId': 1,
                    'Number': '$busNumber',
                    'Driver Name': {'$ifNull': [ '$driverData.driverName', 0 ]},
                    'Route Name': {'$ifNull': [ '$routeData.areaName', 0 ]},
                    'Sub Route Name': {'$ifNull': [ '$routeData.routeName', 0 ]},
                    'Bus Running': '$busRunningStatus',
                    'Device Id': "$allotedDeviceId"
                }
            }
        ]
        return json_util.loads(json_util.dumps(self.vehiclesCol.aggregate(pipeline)))

    def reformatRoutesData(self):
        # Define the pipeline for the aggregation
        pipeline = [
            {
                '$lookup': {
                    'from': 'vehicles',  # collection to join
                    'localField': 'allotedBusId',  # field from the first table
                    'foreignField': 'busId',  # field from the second table
                    'as': 'busData'  # alias for the joined data
                }
            },
            {
                '$unwind': {
                    "path": "$busData",
                    "preserveNullAndEmptyArrays": True
                }  # deconstruct the array field
            },
            {
                '$project': {
                    '_id': 0,
                    'routeId': 1,
                    'Name': '$areaName',
                    'Sub Name': '$routeName',
                    'Number of Stages': {'$size': '$routeStageWithNames'},
                    'Total Distance': '$totalRouteDistance',
                    'Bus No': {'$ifNull': [ '$busData.busNumber', 0 ]}
                }
            }
        ]
        return json_util.loads(json_util.dumps(self.routesCol.aggregate(pipeline)))

    def reformatDriversData(self):
        # Define the pipeline for the aggregation
        pipeline = [
            {
                '$lookup': {
                    'from': 'vehicles',  # collection to join
                    'localField': 'allotedBusId',  # field from the first table
                    'foreignField': 'busId',  # field from the second table
                    'as': 'busData'  # alias for the joined data
                }
            },
            {
                '$unwind': {
                    "path": "$busData",
                    "preserveNullAndEmptyArrays": True
                }  # deconstruct the array field
            },
            {
                '$project': {
                    '_id': 0,
                    'driverId': 1,
                    'Name': '$driverName',
                    'Mobile': '$driverMobile',
                    'Address': '$driverAddress',
                    'Bus No': {'$ifNull': [ '$busData.busNumber', 0 ]}
                }
            }
        ]
        return json_util.loads(json_util.dumps(self.driversCol.aggregate(pipeline)))

    def reformatDevicesData(self):
        # Define the pipeline for the aggregation
        pipeline = [
            {
                '$lookup': {
                    'from': 'vehicles',  # collection to join
                    'localField': 'allotedBusId',  # field from the first table
                    'foreignField': 'busId',  # field from the second table
                    'as': 'busData'  # alias for the joined data
                }
            },
            {
                '$unwind': {
                    "path": "$busData",
                    "preserveNullAndEmptyArrays": True
                }  # deconstruct the array field
            },
            {
                '$project': {
                    '_id': 0,
                    'deviceId': 1,
                    'Device Id': '$deviceId',
                    'Bus No': {'$ifNull': [ '$busData.busNumber', 0 ]}
                }
            }
        ]
        return json_util.loads(json_util.dumps(self.devicesCol.aggregate(pipeline)))

    def updateDeviceStatus(self, busId, status):
        self.devicesCol.update_one({"allotedBusId": busId}, {"$set": {"deviceActiveStatus": status}})
        self.vehiclesCol.update_one({"busId": busId}, {"$set": {"busRunningStatus": status}})

    def updateUserConnStatus(self, busId, userId, status):
        if status:
            self.vehiclesCol.update_one({"busId": busId}, {"$inc": {"connCount": 1}})
        else:
            self.vehiclesCol.update_one({"busId": busId}, {"$inc": {"connCount": -1}})
        self.usersCol.update_one({"userId": userId}, {"$set": {"connStatus": status}})

    def addStudentfavourite(self, userId, favouriteBusId):
        user = self.usersCol.find_one({"userId": userId}, {"favourite": 1, "_id": 0})
        if user [ 'favourite' ] == favouriteBusId:
            return 1
        if user [ 'favourite' ] != None or user [ 'favourite' ] != "":
            self.vehiclesCol.update_one({"busId": user [ 'favourite' ]}, {"$inc": {"totalStudentsOpt": -1}})
        self.vehiclesCol.update_one({"busId": favouriteBusId}, {"$inc": {"totalStudentsOpt": 1}})
        self.usersCol.update_one({"userId": userId}, {"$set": {"favourite": favouriteBusId}})

    def fetchRouteLocation(self, busId):
        location = self.routesCol.find_one({"allotedBusId": busId}, {"lastUpdatedLoc": 1})
        if location [ 'lastUpdatedLoc' ] == [ ]:
            print("No location found")
            return self.getAllStagesCoords(busId) [ 0 ] [ 'stageCoord' ]
        return location [ 'lastUpdatedLoc' ] [ -1 ]

    async def updateNewLocation(self, location: list, busId):
        self.routesCol.update_one({"allotedBusId": busId},
                                  {"$push": {"lastUpdatedLoc": {"$each": [ location ], "$slice": -10}}})
        return True

    def getAllStagesCoords(self, busId):
        AllStages = self.routesCol.find_one({"allotedBusId": busId}, {"routeStageWithNames": 1})
        return AllStages [ 'routeStageWithNames' ]

    def gettotalDistance(self, busId):
        totalDistance = self.routesCol.find_one({"allotedBusId": busId}, {"totalRouteDistance": 1})
        return totalDistance [ 'totalRouteDistance' ]

    def getCurStage(self, busId):
        curStage = self.routesCol.find_one({"allotedBusId": busId}, {"curStage": 1})
        return curStage [ 'curStage' ]

    def updateCurStage(self, busId, curStage):
        self.routesCol.update_one({"allotedBusId": busId}, {"$set": {"curStage": curStage}})

    def getLastTwoLOcations(self, busId):
        lastTwoLOcations = self.routesCol.find_one({"allotedBusId": busId}, {"lastUpdatedLoc": 1})
        if lastTwoLOcations [ 'lastUpdatedLoc' ] == [ ] or len(lastTwoLOcations [ 'lastUpdatedLoc' ]) < 2:
            return False
        return lastTwoLOcations [ 'lastUpdatedLoc' ] [ -1:-3:-1 ]

    def getVehicleDirection(self, busId):
        vehicleDirection = self.routesCol.find_one({"allotedBusId": busId}, {"busMoveDirection": 1})
        return vehicleDirection [ 'busMoveDirection' ]

    def updateBusDirection(self, busId, direction):
        self.routesCol.update_one({"allotedBusId": busId}, {"$set": {"busMoveDirection": direction}})
        return True

    def updateStagesDetails(self, busId, stageDetails):
        self.routesCol.update_one({"allotedBusId": busId},
                                  {"$push": {f"routeStageVisitInfo.{getCurrentDateForDb()}": {"$each": [ stageDetails ],
                                                                                              "$slice": -10}}},
                                  upsert=True)

    async def getLatestStageDetails(self, busId):
        latestStage = self.routesCol.find_one({"allotedBusId": busId},
                                              {f"routeStageVisitInfo.{getCurrentDateForDb()}": 1, "_id": 0})
        if latestStage [ 'routeStageVisitInfo' ]:
            return latestStage [ 'routeStageVisitInfo' ] [ getCurrentDateForDb() ] [ -1 ]
        return {
            "curStage": 0,
            "percentageSubRoute": 0,
            "coveredSubDistance": 0,
            "remainSubDistance": 0,
            "moveDirection": "DOWN",
            "location": self.fetchRouteLocation(busId),
            "speed": 0
        }
