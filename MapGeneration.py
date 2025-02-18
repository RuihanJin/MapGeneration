from collections import deque
from enum import Enum

from TIN import *
from Utils import *
from PerlinNoise import PerlinNoise


### TYPE OF DISTRICTS

class DistrictType(Enum):
    BLANK           = 1
    OCEAN           = 2
    SEA             = 3
    SHALLOWSEA      = 4
    LAND            = 5
    BARE            = 6
    SCORCHED        = 7
    TUNDRA          = 8
    ICEFIELD        = 9
    TEMPERATEDESERT = 10
    DESERT          = 11
    GRASSLAND       = 12
    SHRUBLAND       = 13
    TAIGA           = 14
    FOREST          = 15
    RAINFOREST      = 16
    LAKE            = 17
    COASTLINE       = 18


### TYPE OF LINES

class LineType(Enum):
    BLANK           = 1
    BEACH           = 2
    REEF            = 3
    MUD             = 4
    MARSH           = 5
    MANGROVE        = 6
    ICECOAST        = 7
    RIVER           = 8


colorMapping = {
    DistrictType.BLANK: (255, 255, 255),
    DistrictType.OCEAN: (0, 0, 205),
    DistrictType.SEA: (25, 134, 225),
    DistrictType.SHALLOWSEA: (135, 206, 245),
    DistrictType.LAND: (81, 58, 42),
    DistrictType.BARE: (187, 187, 187),
    DistrictType.SCORCHED: (153, 153, 153),
    DistrictType.TUNDRA: (201, 201, 171),
    DistrictType.ICEFIELD: (240, 255, 255),
    DistrictType.TEMPERATEDESERT: (208, 212, 182),
    DistrictType.DESERT: (225, 216, 126),
    DistrictType.GRASSLAND: (153, 180, 112),
    DistrictType.SHRUBLAND: (153, 166, 139),
    DistrictType.TAIGA: (134, 162, 135),
    DistrictType.FOREST: (94, 146, 87),
    DistrictType.RAINFOREST: (66, 118, 85),
    DistrictType.LAKE: (152, 235, 245),
    LineType.BLANK: (0, 0, 0),
    LineType.BEACH: (245, 236, 138),
    LineType.REEF: (80, 90, 70),
    LineType.MUD: (106, 122, 73),
    LineType.MARSH: (133, 160, 102),
    LineType.MANGROVE: (86, 136, 90),
    LineType.ICECOAST: (235, 255, 255),
    LineType.RIVER: (145, 218, 245)
}


class Corner(object):
    def __init__(self, site):
        self.site = site
        self.latitude = None
        self.altitude = None
        self.temperature = None
        self.rainfall = None
        self.gradient = -float("inf")
        self.gradient_direction = None
        self.gradient_district_site = None


class Line(object):
    def __init__(self, sites, width=2, biome=LineType.BLANK):
        self.sites = sites
        self.temperature = 0
        self.rainfall = 0
        self.width = width
        self.biome = biome
        self.is_coastline = False
    
    def update(self):
        self.color_hex = colorHex(colorMapping[self.biome])
        self.line = []
        for site in self.sites:
            self.line.extend([site.x, site.y])
    
    def setCoastlineType(self):
        p = random.random()
        if self.is_coastline:
            if self.temperature < -30:
                self.biome = LineType.ICECOAST
            elif self.temperature < -20:
                if self.rainfall > 500:
                    self.biome = LineType.ICECOAST
                else:
                    self.biome = LineType.REEF  if p > 0.5 else LineType.ICECOAST
            elif self.temperature < 0:
                if self.rainfall > 1500:
                    self.biome = LineType.MANGROVE if p > 0.8 else LineType.MARSH
                elif self.rainfall > 500:
                    self.biome = LineType.MARSH if p > 0.3 else LineType.MUD
                else:
                    self.biome = LineType.REEF if p > 0.3 else LineType.MARSH
            elif self.temperature < 20:
                if p < 0.075 or self.rainfall <= 500:
                    self.biome = LineType.BEACH
                elif self.rainfall > 3200:
                    self.biome = LineType.MANGROVE  if p > 0.5 else LineType.MARSH
                elif self.rainfall > 1200:
                    self.biome = LineType.MARSH if p > 0.5 else LineType.MUD
                else:
                    self.biome = LineType.REEF if p > 0.5 else LineType.MARSH
            else:
                if p < 0.15 or self.rainfall <= 500:
                    self.biome = LineType.BEACH
                elif self.rainfall > 2500:
                    self.biome = LineType.MANGROVE  if p > 0.3 else LineType.MARSH
                elif self.rainfall > 1000:
                    self.biome = LineType.MARSH  if p > 0.8 else LineType.MUD
                else:
                    self.biome = LineType.REEF if p > 0.8 else LineType.MUD


class District(object):
    def __init__(self, site, voronoi, biome=DistrictType.BLANK):
        self.site = site
        self.voronoi = voronoi
        self.latitude = 0
        self.altitude = 0
        self.temperature = 0
        self.rainfall = 0
        self.biome = biome
        self.is_continental = True
        self.is_coast = False
        self.is_basin = False
    
    def update(self):
        # prepare for painting fill color
        self.color_hex = colorHex(colorMapping[self.biome])
        self.borders = []
        for site in self.voronoi:
            self.borders.extend([site.x, site.y])
    
    def isOceanic(self):
        return self.biome in (DistrictType.OCEAN, DistrictType.SEA, DistrictType.SHALLOWSEA)
    
    def getCommonBorder(self, other_district):
        common_sites = []
        other_voronoi = other_district.voronoi
        for self_site in self.voronoi:
            for other_site in other_voronoi:
                if self_site == other_site:
                    common_sites.append(self_site)
                    break
        common_border = Line(common_sites)
        return common_border
    
    def setLandDistrictType(self):
        p = random.random()
        if not self.isOceanic():
            if self.temperature < -30:
                if self.rainfall > 500:
                    self.biome = DistrictType.ICEFIELD
                elif self.rainfall > 200:
                    self.biome = DistrictType.ICEFIELD if p > 0.2 else DistrictType.BARE
                else:
                    self.biome = DistrictType.ICEFIELD if p > 0.4 else DistrictType.SCORCHED
            elif self.temperature < -20:
                if self.rainfall > 800:
                    self.biome = DistrictType.ICEFIELD if p > 0.2 else DistrictType.TUNDRA
                elif self.rainfall > 500:
                    self.biome = DistrictType.ICEFIELD if p > 0.5 else DistrictType.TUNDRA
                else:
                    self.biome = DistrictType.BARE if p > 0.5 else DistrictType.SCORCHED
            elif self.temperature < 0:
                if self.rainfall > 2000:
                    self.biome = DistrictType.TAIGA
                elif self.rainfall > 1000:
                    self.biome = DistrictType.TAIGA if p > 0.3 else DistrictType.SHRUBLAND
                elif self.rainfall > 500:
                    self.biome = DistrictType.SHRUBLAND if p > 0.3 else DistrictType.TEMPERATEDESERT
                elif self.rainfall > 200:
                    self.biome = DistrictType.SHRUBLAND if p > 0.7 else DistrictType.TEMPERATEDESERT
                else:
                    self.biome = DistrictType.TEMPERATEDESERT if p > 0.7 else DistrictType.DESERT
            elif self.temperature < 20:
                if self.rainfall > 3000:
                    self.biome = DistrictType.RAINFOREST if p > 0.3 else DistrictType.FOREST
                elif self.rainfall > 1500:
                    self.biome = DistrictType.FOREST if p > 0.3 else DistrictType.GRASSLAND
                elif self.rainfall > 300:
                    self.biome = DistrictType.GRASSLAND if p > 0.3 else DistrictType.TEMPERATEDESERT
                else:
                    self.biome = DistrictType.TEMPERATEDESERT if p > 0.7 else DistrictType.DESERT
            else:
                if self.rainfall > 3000:
                    self.biome = DistrictType.RAINFOREST if p > 0.1 else DistrictType.FOREST
                elif self.rainfall > 1200:
                    self.biome = DistrictType.FOREST if p > 0.1 else DistrictType.GRASSLAND
                elif self.rainfall > 500:
                    self.biome = DistrictType.GRASSLAND if p > 0.1 else DistrictType.TEMPERATEDESERT
                else:
                    self.biome = DistrictType.DESERT


class MapGeneration(object):
    def __init__(self, width, height, sites, sea_level=2, min_latitude=-1, max_latitude=1, island_num=1, lake_coastline_check=True, river_generate=True):
        self.width = width
        self.height = height
        self.builder = TIN(maxx=self.width, maxy=self.height)
        self.sites = sites
        self.corners = {}
        self.districts = {}
        self.coastlines = []
        self.rivers = []
        self.estuaries = set()
        self.sea_level = max(sea_level, 0)
        self.min_latitude = min_latitude
        self.max_latitude = max_latitude
        self.max_temperature = 40
        self.min_temperature = -40
        self.max_rainfall = 4000
        self.min_rainfall = 0
        self.island_num = island_num
        self.lake_coastline_check = lake_coastline_check
        self.river_generate = river_generate

        # randomly set the center of islands
        self.island_x = [random.uniform(self.width / 5, 4 * self.width / 5) for _ in range(self.island_num)]
        self.island_y = [random.uniform(self.height / 5, 4 * self.height / 5) for _ in range(self.island_num)]
        self.island_elevation = [random.uniform(1, 4) for _ in range(self.island_num)]
        self.island_area = [random.uniform(1 / 9, 1 / 25) for _ in range(self.island_num)]

    def process(self):
        for i in range(len(self.sites)):
            self.sites[i].sitenum = i
            edge = self.builder.insertSite(self.sites[i])

    def updatePoints(self):
        self.process()
        voronoi_list = []
        for site in self.sites:
            voronoi = self.builder.getSiteVoronoi(site)
            voronoi_list.append(voronoi)
        self.sites.clear()
        for voronoi in voronoi_list:
            center = Site(0.0, 0.0)
            for corner in voronoi:
                center = center + corner
            center = center / len(voronoi)
            if self.isValidPoint(center):
                self.sites.append(center)
        # Reset the TIN Builder
        self.builder = TIN(maxx=self.width, maxy=self.height)
        return self.sites
    
    def isValidPoint(self, point):
        return (0 < point.x < self.width) and (0 < point.y < self.height)
    
    def getDistricts(self):
        return list(self.districts.values())
    
    def getNeighborDistricts(self, district):
        neighbor_sites = self.builder.getSiteDelaunay(district.site)
        neighbor_districts = [self.districts[site] for site in neighbor_sites if site in self.districts]
        return neighbor_districts
    
    def generateDistricts(self):
        # re-order the districts
        self.sites = sorted(self.sites, key=lambda d: d.x + d.y)
        for center_site in self.sites:
            voronoi = self.builder.getSiteVoronoi(center_site)
            if self.river_generate:
                highest_corner = None
                highest_altitude = -float("inf")
                for corner_site in voronoi:
                    corner = Corner(site=corner_site)
                    if corner_site not in self.corners:
                        # set geographical arrtibute
                        self.setLatitude(corner)
                        self.setAltitude(corner)
                        self.setTemperature(corner)
                        self.setRainfall(corner)
                        self.corners[corner_site] = corner
                    corner = self.corners[corner_site]
                    if corner.altitude > highest_altitude:
                        highest_corner = corner_site
                        highest_altitude = corner.altitude
                for corner_site in voronoi:
                    corner = self.corners[corner_site]
                    if highest_altitude > corner.gradient:
                        corner.gradient = highest_altitude
                        corner.gradient_direction = highest_corner
                        corner.gradient_district_site = center_site
            else:
                for corner_site in voronoi:
                    corner = Corner(site=corner_site)
                    if corner_site not in self.corners:
                        # set geographical arrtibute
                        self.setLatitude(corner)
                        self.setAltitude(corner)
                        self.setTemperature(corner)
                        self.setRainfall(corner)
                        self.corners[corner_site] = corner
            district = District(site=center_site, voronoi=voronoi)
            # calculate geographical arrtibute
            self.calculateGeographicalAttribute(district)
            # set geomorphic attribute
            self.setSeaDistrictType(district)
            district.setLandDistrictType()
            # avoid generate rivers on ocean
            if self.river_generate:
                if district.isOceanic():
                    for corner_site in district.voronoi:
                        corner = self.corners[corner_site]
                        corner.gradient = -float("inf")
                        corner.gradient_direction = corner_site
            self.districts[center_site] = district
        # set global geomorphic attribute
        if self.lake_coastline_check:
            self.setLakeAndCoastline()
            # set geomorphic attribute for coastlines
            self.setCoastlineType()
        if self.river_generate:
            self.setRiver()

        # update
        for site in self.sites:
            self.districts[site].update()
        for coastline in self.coastlines:
            coastline.update()
        for river in self.rivers:
            river.update()
    
    # Geographical Attribute

    def normalizedEuclideanDistance(self, x1, y1, x2, y2):
        """Calculates the normalized Euclidean distance between two points
        :return's value range: [0, √2]
        """
        dx = (x1 - x2) / self.width
        dy = (y1 - y2) / self.height
        return math.sqrt(dx*dx + dy*dy)

    def setLatitude(self, corner):
        delta = (self.height - corner.site.y) / self.height
        corner.latitude = self.min_latitude + (self.max_latitude - self.min_latitude) * delta
    
    def randomAltitude(self, x, y):
        island_altitude = 0
        for island_x, island_y, island_elevation, island_area in zip(self.island_x, self.island_y, self.island_elevation, self.island_area):
            island_altitude += island_elevation * max(1 - self.normalizedEuclideanDistance(x, y, island_x, island_y) ** 2 / island_area, 0)
        noise_altitude = PerlinNoise(x, y, 0)
        altitude = island_altitude + noise_altitude - self.sea_level
        return altitude

    def setAltitude(self, corner):
        site = corner.site
        corner.altitude = self.randomAltitude(site.x, site.y)
    
    def setTemperature(self, corner):
        temperature = self.min_temperature + (self.max_temperature - self.min_temperature) * math.cos(corner.latitude * math.pi / 2) - 8 * max(corner.altitude, 0)
        corner.temperature = temperature
    
    def setRainfall(self, corner):
        rainfall = self.min_rainfall + (self.max_rainfall - self.min_rainfall) * rainfallCurve(corner.latitude) - 120 * max(corner.altitude, 0)
        corner.rainfall = rainfall
    
    def calculateGeographicalAttribute(self, district):
        num_corner = len(district.voronoi)
        for corner_site in district.voronoi:
            corner = self.corners[corner_site]
            district.latitude += corner.latitude
            district.altitude += corner.altitude
            district.temperature += corner.temperature
            district.rainfall += corner.rainfall
        district.latitude /= num_corner
        district.altitude /= num_corner
        district.temperature /= num_corner
        district.rainfall /= num_corner

    # Geomorphic Attribute

    def setSeaDistrictType(self, district):
        if district.altitude > 0:
            district.biome = DistrictType.LAND
        elif district.altitude > - self.sea_level + 1.2:
                district.biome = DistrictType.SHALLOWSEA
        elif district.altitude > - self.sea_level + 0.1:
            voronoi = district.voronoi
            for site in voronoi:
                if not self.isValidPoint(site):
                    district.biome = DistrictType.OCEAN
                    return
            district.biome = DistrictType.SEA
        else:
            district.biome = DistrictType.OCEAN

    def setLakeAndCoastline(self):
        q = deque()
        first_oceanic_district = None
        for site in self.sites:
            district = self.districts[site]
            if district.isOceanic():
                district.is_continental = False
                first_oceanic_district = district
                break
        if first_oceanic_district:
            q.append(first_oceanic_district)
            while q:
                district = q.popleft()
                neighbor_sites = self.builder.getSiteDelaunay(district.site)
                for neighbor_site in neighbor_sites:
                    neighbor_district = self.districts.get(neighbor_site)
                    if neighbor_district and neighbor_district.is_continental:
                        if neighbor_district.isOceanic():
                            neighbor_district.is_continental = False
                            q.append(neighbor_district)
                        else:
                            coastline = district.getCommonBorder(neighbor_district)
                            coastline.is_coastline = True
                            coastline.width = random.randint(1, 3)
                            self.coastlines.append(coastline)
                            # update district type of the coast
                            if not neighbor_district.is_coast:
                                neighbor_district.is_coast = True
                                neighbor_district.rainfall += 200
                                neighbor_district.setLandDistrictType()
            for site in self.sites:
                district = self.districts[site]
                if district.isOceanic() and district.is_continental:
                    district.biome = DistrictType.LAKE
                    for corner_site in district.voronoi:
                        self.estuaries.add(corner_site)
    
    def setCoastlineType(self):
        for coastline in self.coastlines:
            for corner_site in coastline.sites:
                corner = self.corners[corner_site]
                coastline.temperature += corner.temperature
                coastline.rainfall += corner.rainfall
            coastline.temperature /= 2
            coastline.rainfall /= 2
            # set coastline type
            coastline.setCoastlineType()
    
    def setRiver(self):
        for coastline in self.coastlines:
            for corner_site in coastline.sites:
                self.estuaries.add(corner_site)
        self.estuaries = list(self.estuaries)
        for estuary in self.estuaries:
            downstream = estuary
            upstream = self.corners[estuary].gradient_direction
            # start condition
            p = random.random()
            if p > 0.4:
                width = random.randint(1, 3)
                while upstream != downstream:
                    q = random.random()
                    river_corner = self.corners[upstream]
                    # end condition
                    if q > 0.9 or (upstream in self.estuaries) or (river_corner.temperature < -10) or (river_corner.rainfall < 300):
                        break
                    river = Line([downstream, upstream], width=width, biome=LineType.RIVER)
                    self.rivers.append(river)
                    # update district type along the river
                    basin_district = self.districts[self.corners[downstream].gradient_district_site]
                    if not basin_district.is_basin:
                        basin_district.is_basin = True
                        basin_district.rainfall += 400
                        basin_district.setLandDistrictType()
                    downstream = upstream
                    upstream = river_corner.gradient_direction
