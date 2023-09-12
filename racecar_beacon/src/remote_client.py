#!/usr/bin/env python

import socket
from struct import * # Import struct to use unpack
import sys

HOST = '127.0.0.1'
# This process should listen to a different port than the PositionBroadcast client.
PORT = 65432

positionFormat = "fffxxxx" # Format is three 32-bit floats and four empty bytes for position of vehicule
obstacleFormat = "Ixxxxxxxxxxxx" # Format is one 32-bit integer and twelve empty bytes
idFormat = "Ixxxxxxxxxxxx" # Format is one 32-bit integer and twelve empty bytes
userInputFormat = "4s"

racecarSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket uses IPv4 and is a TCP socket (Connexion has to be established; message integrity assured with ACK)
racecarSocket.connect((HOST, PORT)) # Connect the socket to the host and port (block here until a connection is established)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

while True:
	userInput = input("Entrer une commande :") # Prompts user to enter command (RPOS, OBSF or RBID)
	if userInput == "RPOS":
		userInputPack = pack(userInputFormat,userInput.encode())
		racecarSocket.send(userInputPack) # Send vehicule position
		vehiculePos = recvall(racecarSocket, 16) # Receive data from the socket (TCP)
		vehiculePosUnpack = unpack(positionFormat,vehiculePos) # Convert binary to string
		print(vehiculePosUnpack)
	elif userInput == "OBSF":
		userInputPack = pack(userInputFormat,userInput.encode())
		racecarSocket.send(userInputPack) # Send vehicule position
		vehiculeObstacle = recvall(racecarSocket, 16) # Receive data from the socket (TCP)
		vehiculeObstacleUnpack = unpack(obstacleFormat,vehiculeObstacle) # Convert binary to string
		print(vehiculeObstacleUnpack)
	elif userInput == "RBID":
		userInputPack = pack(userInputFormat,userInput.encode())
		racecarSocket.send(userInputPack) # Send vehicule position
		vehiculeId = recvall(racecarSocket, 16) # Receive data from the socket (TCP)
		vehiculeIdUnpack = unpack(idFormat,vehiculeId) # Convert binary to string
		print(vehiculeIdUnpack)
	elif userInput == "EXIT" :
		userInputPack = pack(userInputFormat,userInput.encode())
		racecarSocket.send(userInputPack) # Send vehicule position
		racecarSocket.close() # Close the socket connection when the loop is exited
		break
	else :
		print("La donnée n’est pas disponible")
		
sys.exit()