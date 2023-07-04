import os
import json
import math

# Title: FAA .DAT STARS VideoMap to GeoJSON conversion tool
# Author: Max Gorodetzki (MO)
# Copyright (c) 4 July 2023


C_DIR = os.getcwd()
CONVERT_LIST = []
EXPORT_LIST = []
maximum_draw = int(input("Enter maximum range to draw: "))

# Function takes a split line string from the convert function as an input and returns an array of the
# decimal degree values in [longitude, latitude] format where longitude and latitude are type float


def dmstodecimaldegrees(line: list):
    D2 = int(line[1]) + int(line[2]) / 60 + float(line[3]) / 3600
    D1 = -1 * (int(line[4]) + int(line[5]) / 60 + float(line[6]) / 3600)
    return [D1, D2]


# Function distance calculates the distance between two points on the earth using the Haversine formula
# Output is a float.


def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    c = math.cos
    a = (
        0.5
        - c((lat2 - lat1) * p) / 2
        + c(lat1 * p) * c(lat2 * p) * (1 - c((lon2 - lon1) * p)) / 2
    )
    return 7917.6 * math.asin(math.sqrt(a))


# Function convert opens a file from the path specified at index 0 of file and returns an array of line arrays to
# be processed into the GeoJSON format. Returns an array with the processed lines and the center of the videomap.


def convert(file: list):
    initial = True
    flagstart = False
    LINES = []
    CENTER = []
    with open(file[0], "r") as fx:
        SEGMENT = []
        while True:
            line = fx.readline()
            if not line:
                break
            splits = line.split()
            if splits[0] == "LINE" and not flagstart:
                flagstart = True
            if splits[0] == "GP" and initial:
                initial = False
                CENTER = dmstodecimaldegrees(splits)
            if splits[0] == "GP" and not initial:
                SEGMENT.append(dmstodecimaldegrees(splits))
            if splits[0] == "LINE" and flagstart:
                flagstart = False
                LINES.append(SEGMENT)
                SEGMENT = []
    fx.close()
    return [LINES, CENTER]


# Function generategeojson takes the output of the convert function as an argument (list) and processes it into a GeoJSON formatted dictionary
# that can be exported into a file.


def generategeojson(export: list):
    TEMPLATE = {"type": "FeatureCollection", "features": []}
    CENTER = export[1]
    for coordlist in export[0]:
        checkf = True
        for pair in coordlist:
            lon1 = pair[0]
            lat1 = pair[1]
            lon2 = CENTER[0]
            lat2 = CENTER[1]
            d = distance(lat1, lon1, lat2, lon2)
            if d > maximum_draw:
                checkf = False
                break
        if len(coordlist) > 0 and checkf:
            TEMPLATE["features"].append(
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coordlist},
                    "properties": {
                        "color": "#505028",
                        "style": "solid",
                        "thickness": 1,
                    },
                }
            )
    return TEMPLATE


filelist = os.listdir()
for i in filelist:
    ft = i.split(".")[-1]
    if ft == "dat":
        CONVERT_LIST.append([C_DIR + "\\" + i, i])
for file in CONVERT_LIST:
    z = [file[1], convert(file)]
    EXPORT_LIST.append(z)
    print(
        f"Converted file #{CONVERT_LIST.index(file)+1}/{len(CONVERT_LIST)}! [{file[1]}]"
    )
print("~~~CONVERSIONS COMPLETE~~~")
for export in EXPORT_LIST:
    name = export[0]
    ex = generategeojson(export[1])
    with open(C_DIR + "\\" + name.split(".")[0] + ".geojson", "x") as zfile:
        json.dump(ex, zfile)
    zfile.close()
    print(
        f"Exported file #{EXPORT_LIST.index(export)+1}/{len(EXPORT_LIST)}! [{export[0].split('.')[0] + '.geojson'}]"
    )
print("~~~EXPORTS COMPLETE~~~")
