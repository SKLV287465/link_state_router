# Link State Routing Assignment 1
# By Joshua Shim z5479929 on 2nd Febuary 2024

import sys
import socket
import time
import threading
import LinkStatePacket as lsp

# constants used to index distance and port within tuple.
PORT = 1
DISTANCE = 0

ROUTER_ID = sys.argv[1]
ROUTER_PORT = sys.argv[2]
CONFIG_FILE = open(sys.argv[3], "r")
UPDATE_INTERVAL = 1
ROUTE_UPDATE_INTERVAL = 30
ADDRESS = "127.0.0.1" 

# Graph implementation as dictionary adjacency list
adjList = {}

lastPacketTime = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ADDRESS, int(ROUTER_PORT)))

# Config file:
"""
1. add adjacent nodes to dictionary
this works
"""
def configFile():
    adjList[ROUTER_ID] = {}
    lineCounter = 0
    for line in CONFIG_FILE:
        lineCounter += 1
        if lineCounter == 1:
            continue
        id, cost, port = line.split()
        adjList[ROUTER_ID].update({id: (float(cost), int(port))})
# listen
"""
1. listen from adjacent ports
2. if for 3 seconds no message comes from certain origin turn off list
"""
def listen():

    while True:
        recievedFile = sock.recvfrom(4096)[0].decode('utf-8')
        # update adjList
        packet = lsp.LinkStatePacket.from_json(recievedFile)
        adjList.update({packet.origin: packet.adjInfo})
        lastPacketTime.update({packet.origin: packet.time})
        # relay
        packet.visited.append(ROUTER_ID)
        for key in adjList[ROUTER_ID].keys():
            if key in packet.visited:
                continue
            sock.sendto(packet.to_json().encode('utf-8'), ("127.0.0.1", adjList[ROUTER_ID][key][PORT]))

def send():
    while True:
        for key in adjList[ROUTER_ID].keys():
            sock.sendto((lsp.LinkStatePacket(ROUTER_ID, adjList[ROUTER_ID], [ROUTER_ID]).to_json().encode('utf-8')), ("127.0.0.1", adjList[ROUTER_ID][key][PORT]))
        time.sleep(1)
        lastPacketTime.update({ROUTER_ID: time.time()})

def djikstra():
    while True:
        time.sleep(30)
        # check which routers are turned on
        offNodes = []
        onNodes = []
        for node in adjList.keys():
            if lastPacketTime[ROUTER_ID] - lastPacketTime[node] >= 3:
                offNodes.append(node)
            else:
                onNodes.append(node)
        
        print('I am Router ' + ROUTER_ID)
        for destination in onNodes:
            if destination == ROUTER_ID:
                continue
            
            distances = {node: float('infinity') for node in onNodes}
            pred = {key: ROUTER_ID for key in onNodes}
            distances[ROUTER_ID] = 0
            
            nodeSet = {node for node in onNodes}
            
            while len(nodeSet) > 0:
                # find closest node
                minDist = float("infinity")
                closestNode = None
                for leftoverNode in nodeSet:
                    if distances[leftoverNode] < minDist:
                        minDist = distances[leftoverNode]
                for leftoverNode in nodeSet:
                    if minDist == distances[leftoverNode]:
                        closestNode = leftoverNode
                        break
                
                # relax nodes
                for adjacentNode in adjList[closestNode].keys():
                    if adjacentNode in offNodes or adjacentNode not in onNodes:
                        continue
                    if (distances[adjacentNode] > distances[closestNode] + adjList[closestNode][adjacentNode][DISTANCE]):
                        # relax
                        distances[adjacentNode] = distances[closestNode] + adjList[closestNode][adjacentNode][DISTANCE]
                        pred[adjacentNode] = closestNode
                        
                # end iteration
                nodeSet.remove(closestNode)
            fastestPath = destination
            ptr = destination
            while pred[ptr] != ROUTER_ID:
                fastestPath = pred[ptr] + fastestPath
                ptr = pred[ptr]
            fastestPath = ROUTER_ID + fastestPath 
            print("Least cost path to router " + destination + ": " + fastestPath +  " and the cost is " + str(round(distances[destination], 5)))

def main(argv):

    configFile()


    # Threading
    listeningThread = threading.Thread(target=listen, args=()) # run indefinitely
    sendingThread = threading.Thread(target=send, args=()) # run every second
    djikstraThread = threading.Thread(target=djikstra, args=()) # run every thirty seconds

    listeningThread.start()
    sendingThread.start()
    djikstraThread.start()

main(sys.argv)