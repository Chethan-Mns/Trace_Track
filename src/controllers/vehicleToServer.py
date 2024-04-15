import asyncio
import sys
import time

sys.path.append('src')
from models.vehiSpotDB import VehiSpotDb
from fastapi import WebSocket
from typing import List
import osmnx as ox
import threading
from utill.helperFunctions import calculateTimeToReach


class VehicleToServerConnectionManager:
    def __init__(self):
        self.active_connections: List [ WebSocket ] = [ ]
        self.dbManager = VehiSpotDb()

    async def connect(self, websocket: WebSocket, busId):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.dbManager.updateDeviceStatus(busId, True)

    async def disconnect(self, websocket: WebSocket, busId):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.dbManager.updateDeviceStatus(busId, False)

    async def boardcast_to_web(self, data):
        for conn in self.active_connections:
            try:
                await conn.send_json(data)
            except:
                await self.disconnect(conn, data [ 'busId' ])

    async def boardcast_to_single(self, data, websocket: WebSocket):
        try:
            await websocket.send_json(data)
        except:
            await self.disconnect(websocket, data [ 'busId' ])


class VehicleToServer:
    def __init__(self, busId):
        self.dbManager = VehiSpotDb()
        self.busId = busId
        self.busRoute = RouteStages(self.busId)
        self.i = 0

    def fetchLocation(self):
        location = self.dbManager.fetchRouteLocation(self.busId)
        return location

    def updateBusStageLocation(self, latest_data):
        previous_data = None
        busDirection = None
        if latest_data [ 'vehicleCoord' ] != previous_data:
            stageDetails = self.busRoute.evaluteTheStageProgress(latest_data [ 'vehicleCoord' ],
                                                                 latest_data [ 'speed' ])
            stageDetails [ 'location' ] = latest_data [ 'vehicleCoord' ]
            stageDetails [ 'speed' ] = latest_data [ 'speed' ]
            stageDetails [ 'accuracy' ] = latest_data [ 'accuracy' ]
            self.dbManager.updateStagesDetails(self.busId, stageDetails)
            if busDirection != stageDetails [ 'moveDirection' ]:
                self.dbManager.updateBusDirection(self.busId, stageDetails [ 'moveDirection' ])
                busDirection = stageDetails [ 'moveDirection' ]
            previous_data = latest_data

    async def updateBusNewLocation(self, latest_data):
        if latest_data [ 'accuracy' ] > 20:
            return True
        await self.dbManager.updateNewLocation(latest_data [ 'vehicleCoord' ], self.busId)
        thread = threading.Thread(target=self.updateBusStageLocation, args=(latest_data,))
        thread.start()
        return True


class RouteStages:
    def __init__(self, busId):
        self.busId = busId
        self.dbManager = VehiSpotDb()
        self.stagesWithNames = self.dbManager.getAllStagesCoords(busId)
        self.stages = [ stage [ "stageCoord" ] for stage in self.stagesWithNames ]
        self.totalDistance = self.dbManager.gettotalDistance(busId)
        self.currentStage = self.dbManager.getCurStage(busId)
        self.moveDirection = self.dbManager.getVehicleDirection(busId)

    def findDistance(self, loc1: list, loc2: list):
        distance = ox.distance.great_circle(loc1 [ 0 ], loc1 [ 1 ], loc2 [ 0 ], loc2 [ 1 ])
        return distance

    def findNearestStage(self, loc):
        allStagesDistanceToLoc = {index: self.findDistance(loc, stage) for index, stage in enumerate(self.stages)}
        nearest_stage_index = min(allStagesDistanceToLoc, key=allStagesDistanceToLoc.get)
        return nearest_stage_index, allStagesDistanceToLoc

    def checkMovementDirection(self, calibratePoints: list, referDirection):
        startOne = self.findDistance(self.stages [ 0 ], calibratePoints [ 1 ])
        startTwo = self.findDistance(self.stages [ 0 ], calibratePoints [ 0 ])
        endOne = self.findDistance(self.stages [ -1 ], calibratePoints [ 1 ])
        endTwo = self.findDistance(self.stages [ -1 ], calibratePoints [ 0 ])
        # print("startOne = ", startOne, "endOne = ", endOne, "startTwo =", startTwo, "endTwo =", endTwo)
        if startOne < startTwo and endOne > endTwo:
            return "DOWN"
        elif startTwo < startOne and endTwo > endOne:
            return "UP"
        elif startOne < startTwo and endOne < endTwo:
            totalDistance = self.findDistance(self.stages [ 0 ], self.stages [ -1 ])
            if endTwo > totalDistance:
                return "BUP"
            elif startTwo > totalDistance:
                return "BDOWN"
            else:
                return referDirection
        elif startOne > startTwo and endOne > endTwo:
            totalDistance = self.findDistance(self.stages [ 0 ], self.stages [ -1 ])
            if endOne > totalDistance:
                return "BDOWN"
            elif startTwo > totalDistance:
                return "BUP"
            else:
                return referDirection
        else:
            return referDirection

    async def checkBeforeOrAfterStage(self):
        pass

    def evaluteTheStageProgress(self, loc: list, speed):
        calibratePoints = self.getRecentTwoLocation(self.busId)
        if not calibratePoints:
            return {
                "curStage": 0,
                "percentageSubRoute": 0,
                "coveredSubDistance": 0,
                "remainSubDistance": 0,
                "moveDirection": "DOWN",
                "timeTakenToReach": [ ]
            }
        self.moveDirection = self.checkMovementDirection(calibratePoints, self.moveDirection)
        nearestStageIndexWithAllDistances = self.findNearestStage(loc)
        if self.moveDirection == "DOWN":
            if nearestStageIndexWithAllDistances [ 0 ] < len(self.stages)-1:
                subTotalDistance = self.findDistance(self.stages [ nearestStageIndexWithAllDistances [ 0 ] ],
                                                     self.stages [ nearestStageIndexWithAllDistances [ 0 ]+1 ])
                subTotalDistance -= 10
                if subTotalDistance < nearestStageIndexWithAllDistances [ 1 ] [
                    nearestStageIndexWithAllDistances [ 0 ]+1 ]:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]-1
                else:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]
                if self.currentStage < 0:
                    self.currentStage = 0
                next_stage_coord = self.stages [ self.currentStage+1 ]
                sub_total_distance = self.findDistance(self.stages [ self.currentStage ], next_stage_coord)
                sub_total_distance -= 10
                percentage_sub_route = round(
                    (nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ] / sub_total_distance) * 100)
                remain_sub_distance = sub_total_distance-nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ]
            else:
                subTotalDistance = self.findDistance(self.stages [ nearestStageIndexWithAllDistances [ 0 ] ],
                                                     self.stages [ nearestStageIndexWithAllDistances [ 0 ]-1 ])
                subTotalDistance -= 10
                if subTotalDistance > nearestStageIndexWithAllDistances [ 1 ] [
                    nearestStageIndexWithAllDistances [ 0 ]-1 ]:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]-1
                    next_stage_coord = self.stages [ self.currentStage+1 ]
                    sub_total_distance = self.findDistance(self.stages [ self.currentStage ], next_stage_coord)
                    sub_total_distance -= 10
                    if self.currentStage < 0:
                        self.currentStage = 0
                    percentage_sub_route = round(
                        (nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ] / sub_total_distance) * 100)
                    remain_sub_distance = sub_total_distance-nearestStageIndexWithAllDistances [ 1 ] [
                        self.currentStage ]
                else:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]
                    percentage_sub_route = 100
                    remain_sub_distance = 0



        elif self.moveDirection == "UP":
            if nearestStageIndexWithAllDistances [ 0 ] < len(self.stages)-1:
                subTotalDistance = self.findDistance(self.stages [ nearestStageIndexWithAllDistances [ 0 ] ],
                                                     self.stages [ nearestStageIndexWithAllDistances [ 0 ]+1 ])
                subTotalDistance -= 10
                if subTotalDistance > nearestStageIndexWithAllDistances [ 1 ] [
                    nearestStageIndexWithAllDistances [ 0 ]+1 ]:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]+1
                else:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]
                if self.currentStage >= len(nearestStageIndexWithAllDistances [ 1 ]):
                    self.currentStage = len(nearestStageIndexWithAllDistances [ 1 ])-1
                if self.currentStage != 0:
                    next_stage_coord = self.stages [ self.currentStage-1 ]
                    sub_total_distance = self.findDistance(self.stages [ self.currentStage ], next_stage_coord)
                    sub_total_distance -= 10
                    percentage_sub_route = round(
                        (nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ] / sub_total_distance) * 100)
                    remain_sub_distance = sub_total_distance-nearestStageIndexWithAllDistances [ 1 ] [
                        self.currentStage ]
                else:
                    percentage_sub_route = 100
                    remain_sub_distance = 0
            else:
                subTotalDistance = self.findDistance(self.stages [ nearestStageIndexWithAllDistances [ 0 ] ],
                                                     self.stages [ nearestStageIndexWithAllDistances [ 0 ]-1 ])
                subTotalDistance -= 10
                if subTotalDistance < nearestStageIndexWithAllDistances [ 1 ] [
                    nearestStageIndexWithAllDistances [ 0 ] ]:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]-1
                else:
                    self.currentStage = nearestStageIndexWithAllDistances [ 0 ]
                if self.currentStage < 0:
                    self.currentStage = 0
                next_stage_coord = self.stages [ self.currentStage-1 ]
                sub_total_distance = self.findDistance(self.stages [ self.currentStage ], next_stage_coord)
                sub_total_distance -= 10
                percentage_sub_route = round(
                    (nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ] / sub_total_distance) * 100)
                remain_sub_distance = sub_total_distance-nearestStageIndexWithAllDistances [ 1 ] [
                    self.currentStage ]
        else:
            self.currentStage = nearestStageIndexWithAllDistances [ 0 ]
        coveredDistance = nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ]
        if self.currentStage == 0 and (self.moveDirection == "BDOWN" or self.moveDirection == "BUP"):
            remain_sub_distance = nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ]
            self.currentStage -= 1
            percentage_sub_route = 100
        elif self.currentStage == len(self.stages)-1 and (self.moveDirection == "BDOWN" or self.moveDirection == "BUP"):
            remain_sub_distance = nearestStageIndexWithAllDistances [ 1 ] [ self.currentStage ]
            self.currentStage += 1
            percentage_sub_route = 100
        if self.moveDirection == "UP" or self.moveDirection == "BUP":
            timeTakenList = [ calculateTimeToReach(speed, nearestStageIndexWithAllDistances [ 1 ] [
                distane_index ]) if distane_index in range(self.currentStage+1) else 0 for distane_index in
                              range(len(nearestStageIndexWithAllDistances [ 1 ])) ]
        else:
            timeTakenList = [ calculateTimeToReach(speed, nearestStageIndexWithAllDistances [ 1 ] [
                distane_index ]) if distane_index in range(self.currentStage,
                                                           len(nearestStageIndexWithAllDistances [ 1 ])) else 0 for
                              distane_index in range(len(nearestStageIndexWithAllDistances [ 1 ])) ]
        return {
            "curStage": self.currentStage,
            "percentageSubRoute": round(percentage_sub_route),
            "coveredSubDistance": coveredDistance,
            "remainSubDistance": remain_sub_distance,
            "moveDirection": self.moveDirection,
            "timeTakenToReach": timeTakenList
        }

    async def getMoveDirection(self):
        return self.moveDirection

    def getRecentTwoLocation(self, busId):
        return self.dbManager.getLastTwoLOcations(busId)
