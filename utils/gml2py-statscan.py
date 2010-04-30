#!/usr/bin/python

import re
import sys
import xml.sax

# A simple script which turns a gml file into a set of python dictionaries with
# the same set of information, restricted to a bounding box. The goal is to 
# speed up subsequent processing of the same data as well as to distribute 
# the complexity of parsing an XML file from the complexity of generating a 
# of database suitable for geocoding.

class RoadSegment:
    def __init__(self):
        self.coords = []
        self.left = {}
        self.right = {}

class GMLHandler(xml.sax.ContentHandler):
    def __init__(self, placename, min_lat, min_lng, max_lat, max_lng):
        self.placename = placename

        self.min_lat = min_lat
        self.min_lng = min_lng
        self.max_lat = max_lat
        self.max_lng = max_lng
        
        self.inRoadSegment = False
        self.inRoadLineString = False
        self.curRoadSegment = None
        self.cdata = ""

    def setDocumentLocator(self,loc):
        pass
        
    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name=='RoadSegment':
            self.inRoadSegment = True
            self.curRoadSegment = RoadSegment()
        elif name=='gml:LineString' and self.inRoadSegment:
            self.inRoadLineString = True
        self.cdata = ""

    def endElement(self,name):
        if name=='RoadSegment':
            self.inRoadSegment = False
            inRange = False
            for (lat, lng) in self.curRoadSegment.coords:
                if lat > self.min_lat and lat < self.max_lat and \
                        lng > self.min_lng and lng < self.max_lng:
                    inRange = True
            if inRange:
                self.curRoadSegment.left['placeName'] = self.placename
                self.curRoadSegment.right['placeName'] = self.placename
                print { "left": self.curRoadSegment.left, 
                        "right": self.curRoadSegment.right, 
                        "coords": self.curRoadSegment.coords }

        elif name == 'gml:LineString':
            self.inRoadLineString = False
        # general
        elif name=='name':
            self.curRoadSegment.left['name'] = self.cdata
            self.curRoadSegment.right['name'] = self.cdata
        elif name=='type':
            self.curRoadSegment.left['suffix'] = self.cdata
            self.curRoadSegment.right['suffix'] = self.cdata
        elif name=='direction':
            self.curRoadSegment.left['direction'] = self.cdata
            self.curRoadSegment.right['direction'] = self.cdata
        # left side
        elif name=="addrFmLeft":
            self.curRoadSegment.left['firstNumber'] = int(self.cdata)
        elif name=="addrToLeft":
            self.curRoadSegment.left['lastNumber'] = int(self.cdata)
        # right side
        elif name=="addrFmRight":
            self.curRoadSegment.right['firstNumber'] = int(self.cdata)
        elif name=="addrToRight":
            self.curRoadSegment.right['lastNumber'] = int(self.cdata)
        elif name=='gml:coordinates' and self.inRoadLineString:
            self.curRoadSegment.length = 0.0
            for coordtuple_str in self.cdata.split(" "):
                coordtuple = coordtuple_str.split(",")
                if len(coordtuple) == 2:
                    self.curRoadSegment.coords.append((float(coordtuple[1]), float(coordtuple[0])))

    def characters(self, chars):
        self.cdata += chars

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print "Usage: %s <gml file> <placename> <min lat> <min lng> <max lat> <max lng>" % \
            sys.argv[0]
        exit(1)

    xml.sax.parse(sys.argv[1], GMLHandler(sys.argv[2],
                                          float(sys.argv[3]),
                                          float(sys.argv[4]),
                                          float(sys.argv[5]),
                                          float(sys.argv[6])))

