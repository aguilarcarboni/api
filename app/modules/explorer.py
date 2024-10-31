import requests as rq
import pandas as pd
from app.helpers.logger import logger

class Mars:
    
    def __init__(self):

        logger.announcement('Initializing Mars Explorer', 'info')

        self.manifestUrl = 'https://api.nasa.gov/mars-photos/api/v1/manifests/perseverance/?api_key=kQwoyoXi4rQeY0lXWt1RZln6mLeatlYKLmYfGENB'
        self.manifest = self.getManifestData(self.manifestUrl)
        
        self.sol = self.getSol(self.manifest)

        self.imagesUrl = 'https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/photos?sol='+ str(self.sol) + '&api_key=kQwoyoXi4rQeY0lXWt1RZln6mLeatlYKLmYfGENB'
        self.waypointsUrl = 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json'

        self.images = self.getImages(self.imagesUrl)
        self.coordinates = self.getWaypoints(self.waypointsUrl)

        self.data = {
            'images': self.images,
            'coords': self.coordinates
        }

        logger.announcement('Successfully initialized Mars Explorer', 'success')

    def getManifestData(self,url): # gets manifest data
        self.data = rq.get(url).json()
        self.data = self.data['photo_manifest'] # pandas
        return self.data

    def getSol(self,manifestData):
        self.sol = manifestData['max_sol']
        return self.sol

    def getImages(self,url):

        self.images = []
        self.data = rq.get(url).json()

        self.photos = self.data['photos'] # returns a list of all img dictionaries

        for photo in range(len(self.photos)):
            self.imageURL = self.photos[photo]['img_src'] # retrieves all photos
            if self.photos[photo]['camera']['name'] != 'SKYCAM':
                self.images.append(self.imageURL)

        return self.images

    def getWaypoints(self,url):

        self.coords = []
        self.coord = {}
        self.data = rq.get(url).json()
        self.data = self.data['features']

        for waypoint in range(len(self.data)):
            self.coord = {'lon': float(self.data[waypoint]['properties']['lon']), 'lat': float(self.data[waypoint]['properties']['lat']),'sol':int(self.data[waypoint]['properties']['sol'])}
            self.coords.append(self.coord)
        return self.coords

    def getDistance(self,coordsJson):
        distances = []
        distanceData = coordsJson
        for i in range(len(distanceData)):
            distances.append([distanceData[i]['properties']['dist_m'],distanceData[i]['properties']['sol']])
        distances = pd.DataFrame(distances) #data frame
        return distances
