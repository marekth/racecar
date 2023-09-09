#!/usr/bin/env python

import socket
from struct import * # Import struct to use unpack

HOST = '127.0.0.1'
# This process should listen to a different port than the PositionBroadcast client.
PORT = 65432

positionFormat = "fffxxxx" # Format is three 32-bit floats and four empty bytes for position of vehicule
obstacleFormat = "Ixxxxxxxxxxxx" # Format is one 32-bit integer and twelve empty bytes
idFormat = "Ixxxxxxxxxxxx" # Format is one 32-bit integer and twelve empty bytes

racecarSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket uses IPv4 and is a TCP socket (Connexion has to be established; message integrity assured with ACK)
racecarSocket.connect((HOST, PORT)) # Connect the socket to the host and port (block here until a connection is established)

while True:
	dataFromSocket = racecarSocket.recv(16) # Receive data from the socket (TCP)
	if not dataFromSocket:
		break # Break from loop if connexion is closed by client
	userInput = input("Enter command :") # Prompts user to enter command (RPOS, OBSF or RBID)
	if userInput == "RPOS":
		racecarSocket.send(userInput) # Send vehicule position
		vehiculePos = dataFromSocket# Vehicule position from the socket (TCP)
		vehiculePosUnpack = unpack(positionFormat,vehiculePos) # Convert binary to string
		print(vehiculePosUnpack)
	elif userInput == "OBSF":
		racecarSocket.send(userInput) # Send obstacle status
		vehiculeObstacle = dataFromSocket # Obstacle status from the socket (TCP)
		vehiculeObstacleUnpack = unpack(obstacleFormat,vehiculeObstacle) # Convert binary to string
		print(vehiculeObstacleUnpack)
	elif userInput == "RBID":
		racecarSocket.send(userInput) # Send vehicule ID
		vehiculeId = dataFromSocket # Vehicule ID from the socket (TCP)
		vehiculeIdUnpack = unpack(idFormat,vehiculeId) # Convert binary to string
		print(vehiculeIdUnpack)
	else:
		print("La donnée n’est pas disponible") # Print if there is no information available
		
racecarSocket.close() # Close the socket connection when the loop is exited