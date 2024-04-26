# By Joshua Shim z5479929 on 2nd Febuary 2024

import json
import time

class LinkStatePacket: 

    # def __init__(self, origin, adjInfo):
    #     self.origin = origin
    #     self.adjInfo = adjInfo
    #     self.visited = [origin]

    def __init__(self, origin, adjInfo, visited):
        self.origin = origin
        self.adjInfo = adjInfo
        self.visited = visited
        self.time = time.time()
    
    def to_json(self):
        packet_data = {
            "origin": self.origin,
            "adjInfo": self.adjInfo,
            "visited" : self.visited,
            "time" : self.time
        }
        return json.dumps(packet_data)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(data["origin"], data["adjInfo"], data["visited"])