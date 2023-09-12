#!/usr/bin/env python

import rospy
import socket
import threading

from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

from struct import * # Import struct to use unpack
from tf.transformations import euler_from_quaternion # Import to transform quaternion to yaw


vehiculeFormat = "fffI" # Format is three 32-bit floats for position of vehicule and one 32-bit integer for vehicule ID
positionFormat = "fffxxxx" # Format is three 32-bit floats and four empty bytes for position of vehicule
obstacleFormat = "Ixxxxxxxxxxxx" # Format is one 32-bit integer and twelve empty bytes
idFormat = "Ixxxxxxxxxxxx" # Format is one 32-bit integer and twelve empty bytes

def quaternion_to_yaw(quat):
    # Uses TF transforms to convert a quaternion to a rotation angle around Z.
    # Usage with an Odometry message: 
    #   yaw = quaternion_to_yaw(msg.pose.pose.orientation)
    (roll, pitch, yaw) = euler_from_quaternion([quat.x, quat.y, quat.z, quat.w])
    return yaw

class ROSMonitor:
    def __init__(self):
        # Add your subscriber here (odom? laserscan?):
        # self.sub_odom = rospy.Subcriber(...)
        self.sub_odom = rospy.Subscriber("/racecar/odometry/filtered", Odometry, self.odom_cb) # Subscribe to odometry
        # self.sub_laser = rospy.Subscriber(...)
        self.sub_laser = rospy.Subscriber("/racecar/scan", LaserScan, self.laser_cb) # Subscribe to laser

        # Current robot state:
        self.id = 0xFFFF
        self.pos = (0,0,0)
        self.obstacle = False

        # Params :
        self.remote_request_port = rospy.get_param("remote_request_port", 65432)
        self.pos_broadcast_port  = rospy.get_param("pos_broadcast_port", 65431)

        # Thread for RemoteRequest handling:
        self.rr_thread = threading.Thread(target=self.rr_loop)
        self.rr_thread.start() # Start the thread

        self.racecarSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket uses IPv4 and is a Datagram socket (Message destination unknown; broadcast to all potential listeners)
        self.racecarSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Enable broadcasting on the socket for sending data to multiple devices on the same network segment
        self.racecarSocket.bind(('10.0.1.21',self.pos_broadcast_port)) # Bind to address
        
        self.broadcastFrequency = rospy.Timer(rospy.Duration(1), self.broadcastFrequency_cb) # Broadcast vehicle position at 1 Hz frequency
 
        print("ROSMonitor started.")

    def odom_cb(self, data):
        yaw=quaternion_to_yaw(data.pose.pose.orientation) # Convert quaternion to yaw
        self.pos=(data.pose.pose.position.x,data.pose.pose.position.y,yaw) # Set vehicule position
    def laser_cb(self, data):
        self.obstacle= False
        for distance in data.ranges:
            if (distance < 1) and (distance >= data.range_min) and (distance <= data.range_max): # If distance of obstacle shorter than 1m
                self.obstacle = True # Obstacle detected
    def broadcastFrequency_cb(self, event):
        vehiculePosPack = pack(vehiculeFormat,self.pos[0],self.pos[1],self.pos[2],self.id) # Convert string to binary
        self.racecarSocket.sendto(vehiculePosPack,("10.0.1.21",self.pos_broadcast_port)) # Send vehicule position NEED TO FIND ADDRESS!

    def rr_loop(self):
        # Init your socket here :
        # self.rr_socket = socket.Socket(...)

        self.rr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket uses IPv4 and is a TCP socket (Connexion has to be established; message integrity assured with ACK)
        self.rr_socket.settimeout(None) # Block indefinitely while waiting for data
        self.rr_socket.bind(('10.0.1.21',self.remote_request_port)) # Bind to address

        while True:
            self.rr_socket.listen(1) # Prepare socket to accept one incoming connection at a time
            (clientConnection, clientAddress)= self.rr_socket.accept() # Accept incoming connection and retrieve client socket and address
            
            while True:
                data = clientConnection.recv(16) # Receive data from the socket (TCP)
                if not data:
                    break # Break from loop if connexion is closed by client
                decodedData = data.decode('ascii', 'replace') # Decode byte data to ASCII string with replacement for unrepresentable characters
                if decodedData == "RPOS":
                    vehiculePosPack = pack(positionFormat,self.pos[0],self.pos[1],self.pos[2]) # Convert string to binary
                    clientConnection.send(vehiculePosPack) # Send vehicule position
                elif decodedData == "OBSF":
                    vehiculeObstaclePack = pack(obstacleFormat,self.obstacle) # Convert string to binary
                    clientConnection.send(vehiculeObstaclePack) # Send obstacle status
                elif decodedData == "RBID":
                    vehiculeIdPack = pack(idFormat,self.id) # Convert string to binary
                    clientConnection.send(vehiculeIdPack) # Send vehicule ID
                else:
                    clientConnection.send("La donnée n’est pas disponible") # Print if there is no information available
                    
            clientConnection.close() # Close the socket connection when the loop is exited

if __name__=="__main__":
    rospy.init_node("ros_monitor")

    node = ROSMonitor()

    rospy.spin()


