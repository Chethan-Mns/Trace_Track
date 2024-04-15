import os

from flask import *
import sys

sys.path.append('src')
from controllers.userToServer import userToServer
from dotenv import load_dotenv
from errorHandling.routesErrorHandlingWrapper import asyncWrapper
from middleware.routeTokenValidations import token_required, token_required_admin

load_dotenv()

userToServerController = userToServer()
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config [ 'SECRET_KEY' ] = os.environ.get("secret_key")


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html', error_message="", error_code=404), 404


@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('error.html', error_message="", error_code=500), 500


@app.errorhandler(401)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('error.html', error_message=str(e).split(':') [ 1 ], error_code=401), 401


@app.route('/')
@token_required
@asyncWrapper
def index(current_user):
    allRouteWithBusNumber = userToServerController.reformatB()
    allRouteWithBusNumber = [ x for x in allRouteWithBusNumber if x [ 'Device Id' ] and x [ 'Route Name' ] ]
    uniqueAreaNames = list(set([ bus [ 'Route Name' ] for bus in allRouteWithBusNumber ]))
    return render_template('home.html', allRoutes=allRouteWithBusNumber, allAreas=uniqueAreaNames,
                           current_user=current_user)


@app.route('/login/')
@asyncWrapper
def loginPage():
    return render_template('signInUp.html')


@app.route('/account/verify/', methods=[ 'GET' ])
@asyncWrapper
def verifyPage():
    if "userId" in request.args:
        state, status, msg = userToServerController.activeAccount(request.args [ 'userId' ])
        if state == True:
            return render_template('account-verification-done.html')
        elif status == True:
            return render_template('account-verification-already-done.html')
        else:
            return {"status": False, "msg": "Invalid User ID"}
    return abort(404)


@app.route('/account/action/required/', methods=[ 'GET' ])
@asyncWrapper
def requiredPage():
    return render_template('account-verification-needed.html')


@app.route('/trackVehicleOnMap/<busId>/')
@token_required
@asyncWrapper
def trackVehicleOnMap(current_user, busId):
    bus = userToServerController.getBus(busId)
    routeId = bus [ 'allotedRouteId' ]
    routeData = userToServerController.getRouteDetails(routeId)
    return render_template('trackOnMap.html', stagesOfRoute=routeData [ 'routeStageWithNames' ],
                           allCoords=routeData [ "routeAllCoord" ], busId=busId, current_user=current_user)


@app.route('/trackVehicleOnLine/<busId>/')
@token_required
@asyncWrapper
def trackVehicleOnLine(current_user, busId):
    bus = userToServerController.getBus(busId)
    routeId = bus [ 'allotedRouteId' ]
    routeData = userToServerController.getRouteDetails(routeId)
    return render_template('trackOnLine.html', stagesOfRoute=routeData [ 'routeStageWithNames' ],
                           allCoords=routeData [ "routeAllCoord" ], busId=busId, busNumber=bus [ 'busNumber' ],
                           driverName=userToServerController.getDriver(bus [ 'allotedDriverId' ]) [ 'driverName' ],
                           curStage=routeData [ "curStage" ], current_user=current_user)


@app.route('/createRouteWithStages/')
@token_required_admin
@asyncWrapper
def createRouteWithStages(current_user):
    routeData = None
    if 'rid' in request.args:
        routeData = userToServerController.getRouteDetails(request.args [ 'rid' ],
                                                           filterOut={"_id": 0, "routeStageWithNames": 1, "routeId": 1,
                                                                      "areaName": 1, "routeName": 1})
    print(routeData)
    return render_template('createRouteWithStages.html', routeData=routeData)


@app.route('/demoRecordLocation/<busId>/')
@token_required_admin
@asyncWrapper
def demoRecordLocation(current_user, busId):
    return render_template('index.html', busId=busId)


@app.route('/adminDashboard/')
@token_required_admin
@asyncWrapper
def adminDashboard(current_user):
    allDrivers, allRoutes, allBuses, allDevices = userToServerController.reformatD(), userToServerController.reformatR(), userToServerController.reformatB(), userToServerController.reformatDE()
    totalBuses = len(allBuses)
    activeBuses = len([ x for x in allBuses if x [ 'Bus Running' ] ])
    idleBuses = totalBuses-activeBuses
    return render_template('adminDashboard.html', allDrivers=allDrivers, allRoutes=allRoutes, allBuses=allBuses,
                           allDevices=allDevices, activeBuses=activeBuses, idleBuses=idleBuses, totalBuses=totalBuses,
                           open=request.args.get('open') if 'open' in request.args else 'dashboard',
                           current_user=current_user)


if "__main__" == __name__:
    app.run(debug=True)
