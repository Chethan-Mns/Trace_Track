import serial
import pynmea2
import asyncio
import json
import ssl
import time
from datetime import datetime
from pytz import timezone
import certifi
import websockets
import requests
import socket

# Configure serial port
serial_port = "/dev/ttyAMA0"  # Change this to match your serial port
baud_rate = 115200  # Baud rate of the GPS module
flag = True

# WebSocket server URL
server_uri = "wss://vehispot2.onrender.com/vehicles/EstablishConnectionWithServer/rasp0001/"
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

# Load the certificates authorities via the certifi library
ssl_context.load_verify_locations(certifi.where())

# Open serial port
ser = serial.Serial(serial_port, baud_rate, timeout=0.3)

data_format = {"vehicleCoord": [ ], "message": "New Location", "busId": None, "speed": None, "timestamp": "",
               "accuracy": 0.0}


async def get_ip_address():
    try:
        print("getting Ip Addresss")
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Connect to a remote server (doesn't matter which one)
        s.connect(("8.8.8.8", 80))

        # Get the local IP address of the socket
        ip_address = s.getsockname() [ 0 ]
        print("Ip Address Found:", ip_address)
        return ip_address
    except Exception as e:
        print("Error:", e)
        return None


def getCurrentTime() -> str:
    format = "%d-%m-%Y %H:%M:%S"
    now_utc = datetime.now(timezone('UTC'))
    asia_time = now_utc.astimezone(timezone('Asia/Kolkata'))
    return str(asia_time.strftime(format))


async def getBusIdAndIpAddress():
    while True:
        try:
            response = requests.get('https://vehispot2.onrender.com/vehicles/getBusId/?deviceId=rasp0001')
            responseJson = response.json()
            print(responseJson)
            return responseJson [ 'allotedBusId' ], responseJson [ 'ipAddress' ]
        except requests.exceptions.RequestException as e:
            print(f"Failed to get bus ID and IP address: {str(e)}")
            await asyncio.sleep(5)


async def updateIpAddress(ipAddress: str):
    while True:
        try:
            response = requests.post('https://vehispot2.onrender.com/vehicles/updateDeviceIpAddress/',
                                     json={"deviceId": "rasp0001", "ipAddress": ipAddress})
            responseJson = response.json()
            print(responseJson)
            return responseJson
        except requests.exceptions.RequestException as e:
            print(f"Failed to update IP address: {str(e)}")
            await asyncio.sleep(5)


def get_direction(cog):
    if cog is None:
        return "Unknown"
    elif 0 <= cog < 22.5 or 337.5 <= cog <= 360:
        return "North"
    elif 22.5 <= cog < 67.5:
        return "Northeast"
    elif 67.5 <= cog < 112.5:
        return "East"
    elif 112.5 <= cog < 157.5:
        return "Southeast"
    elif 157.5 <= cog < 202.5:
        return "South"
    elif 202.5 <= cog < 247.5:
        return "Southwest"
    elif 247.5 <= cog < 292.5:
        return "West"
    elif 292.5 <= cog < 337.5:
        return "Northwest"


async def connect_to_server_send_data(uri, busId):
    global flag
    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        # Send a message to the server (optional)
        await websocket.send(json.dumps({"message": "connectionRequest", "busId": busId}))
        while True:
            try:
                while True:
                    if flag:
                        message = await websocket.recv()
                        print(f"Received message from server: {message}")
                        flag = False
                    # Read a line of data from the serial port
                    line = ser.readline().decode('utf-8', errors='ignore').strip()

                    # Check if the line starts with '$GPRMC'
                    if line.startswith('$GPRMC'):
                        try:
                            # Parse the $GPRMC sentence
                            msg = pynmea2.parse(line)

                            # Check if the GPS fix is valid
                            if msg.status == 'A':  # 'A' indicates a valid GPS fix
                                # Extract latitude, longitude, and speed
                                latitude = msg.latitude
                                longitude = msg.longitude
                                speed = msg.spd_over_grnd * 1.852  # Convert speed from knots to km/h
                                # Print the data
                                data_format [ 'vehicleCoord' ] = [ latitude, longitude ]
                                data_format [ 'speed' ] = speed
                                data_format [ 'timestamp' ] = getCurrentTime()
                                data_format [ 'busId' ] = busId
                                # data_format [ 'moveDirection' ] = get_direction(msg.true_course)
                                flag = True
                        except pynmea2.ParseError as e:
                            await websocket.send(
                                json.dumps({'error': str(e), 'busId': busId, "message": "error occurred"}))
                        except Exception as e:
                            await websocket.send(
                                json.dumps({'error': str(e), 'busId': busId, "message": "error occurred"}))

                    # Check if the line starts with '$GPGGA'
                    elif line.startswith('$GPGGA'):
                        try:
                            # Parse the $GPGGA sentence
                            accuracy = line.split(',') [ 8 ]
                            msg = pynmea2.parse(line)

                            latitude = msg.latitude
                            longitude = msg.longitude

                            # Extract accuracy from the HDOP value
                            accuracy = float(accuracy) * 2.5

                            data_format [ 'vehicleCoord' ] = [ latitude, longitude ]
                            data_format [ 'timestamp' ] = getCurrentTime()
                            data_format [ 'busId' ] = busId
                            data_format [ 'accuracy' ] = accuracy
                            flag = True
                        except pynmea2.ParseError as e:
                            await websocket.send(
                                json.dumps({'error': str(e), 'busId': busId, "message": "error occurred"}))
                        except Exception as e:
                            await websocket.send(
                                json.dumps({'error': str(e), 'busId': busId, "message": "error occurred"}))
                    else:
                        continue
                    await websocket.send(json.dumps(data_format))
            except websockets.exceptions.ConnectionClosed:
                print("Connection Is Closed")
                break
            except Exception as e:
                await websocket.send(json.dumps({'error': str(e), 'busId': busId, "message": "error occurred"}))


async def main():
    busId, ipAddress = await getBusIdAndIpAddress()
    newIpAddress = await get_ip_address()
    if ipAddress != newIpAddress:
        await updateIpAddress(newIpAddress)
    await connect_to_server_send_data(server_uri, busId)


# Run the main coroutine
asyncio.run(main())
