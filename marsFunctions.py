import pandas as pd
import numpy as np
import requests as rq


def getManifestData(url): # gets manifest data
    manifestData = rq.get(url).json()
    manifestData = manifestData['photo_manifest'] # pandas
    return manifestData

def getSol(manifestData):
    sol = manifestData['max_sol']
    return sol

def getImages(url):
    images = []
    imagesJson = rq.get(url).json()
    imagesJson = imagesJson['photos'] # returns a list of all img dictionaries
    for j in range(len(imagesJson)):
        imageURL = imagesJson[j]['img_src'] # retrieves all photos
        if imagesJson[j]['camera']['name'] != 'SKYCAM':
            images.append(imageURL)
    return images

def getWaypoints(url):
    coords = []
    coord = {}
    coordsJson = rq.get(url).json()
    coordsJson = coordsJson['features'] # gets all position data
    for i in range(len(coordsJson)):
        coord = {'lon': float(coordsJson[i]['properties']['lon']), 'lat': float(coordsJson[i]['properties']['lat']),'sol':int(coordsJson[i]['properties']['sol'])}
        coords.append(coord) #add coord to list
    return coords

def getDistance(coordsJson):
    distances = []
    distanceData = coordsJson
    for i in range(len(distanceData)):
        distances.append([distanceData[i]['properties']['dist_m'],distanceData[i]['properties']['sol']])
    distances = np.array(distances)
    distances = pd.DataFrame(distances) #data frame
    return distances
