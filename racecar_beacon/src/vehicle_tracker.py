#!/usr/bin/env python

import socket 
from struct import * # Import struct to use unpack

HOST = '127.0.0.1'
# This process should listen to a different port than the RemoteRequest client.
PORT = 65433

vehiculeFormat = "fffI" # Format is three 32-bit floats for position of vehicule and one 32-bit integer for vehicule ID

racecarSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket uses IPv4 and is a Datagram socket (Message destination unknown; broadcast to all potential listeners)
racecarSocket.bind((HOST, PORT)) # Bind the socket to the  host and port

while True:
	(vehiculePos, connectionId) = racecarSocket.recvfrom(16) # Receives vehicule position and vehicule ID from the socket (Datagram)
	vehiculePosUnpack = unpack(vehiculeFormat,vehiculePos) # Convert binary to string
	print("ID du vehicule : ",vehiculePosUnpack[3]) # Print vehicule ID
	print("Position du vehicule : ",vehiculePosUnpack[0], vehiculePosUnpack[1], vehiculePosUnpack[2]) # Print vehicule position
