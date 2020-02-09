import matplotlib.pyplot as plt
import shapely
import random
import math
from mountain import Mountain

class MountainRange:
	def __init__(self, intersection, area_factor):
		self.intersection = intersection
		self.area_factor = area_factor
		self.mountains = []
	
	def plot(self, shape, override=plt):
		# base conditions
		if isinstance(shape, shapely.geometry.LineString):
			override.plot(*shape.xy, color=(0, 0, 0), linewidth=self.area_factor)
			return
		elif isinstance(shape, shapely.geometry.Polygon):
			override.plot(*shape.exterior.xy, color=(0, 0, 0), linewidth=self.area_factor)
			return
		
		# recurse
		if isinstance(shape, shapely.geometry.MultiLineString):
			for line in shape:
				self.plot(line, override=override)
		elif isinstance(shape, shapely.geometry.GeometryCollection):
			for geometry in shape:
				self.plot(geometry, override=override)
		elif isinstance(shape, shapely.geometry.MultiPolygon):
			for polygon in shape:
				self.plot(polygon, override=override)
	
	# this code sucks
	def iterate_boundary(self, parent=None):
		if parent == None:
			parent = self.intersection
		
		if isinstance(parent, shapely.geometry.Point):
			yield (parent.x, parent.y)
		elif isinstance(parent, shapely.geometry.LineString):
			yield (parent.coords[0][0], parent.coords[0][1])
			yield (parent.coords[1][0], parent.coords[1][1])
		elif isinstance(parent, shapely.geometry.Polygon):
			for point in parent.exterior.coords:
				yield point
		else:
			for shape in parent:
				if isinstance(shape, shapely.geometry.MultiLineString):
					for line in shape:
						yield self.iterate_boundary(parent=line)
				elif isinstance(shape, shapely.geometry.GeometryCollection):
					for geometry in shape:
						yield self.iterate_boundary(parent=geometry)
				elif isinstance(shape, shapely.geometry.MultiPolygon):
					for polygon in shape:
						yield self.iterate_boundary(parent=polygon)
				elif isinstance(shape, shapely.geometry.Polygon):
					for point in shape.exterior.coords:
						yield point
				elif isinstance(shape, shapely.geometry.LineString):
					yield (shape.coords[0][0], shape.coords[0][1])
					yield (shape.coords[1][0], shape.coords[1][1])

	def create_mountains(self):
		if len(self.mountains) == 0:
			last_radius = 0
			next_radius = random.randint(math.floor((self.area_factor * 6 - self.area_factor * 1) * 100), 
				math.floor((self.area_factor * 6 + self.area_factor * 1) * 100)) / 100
			for point in self.iterate_boundary():
				if self.__closest_mountain_distance(point) > next_radius:
					mountain = Mountain(point, next_radius, len(self.mountains))
					self.mountains.append(mountain)
					last_radius = next_radius
					next_radius = random.randint(math.floor((self.area_factor * 6 - self.area_factor * 1) * 100), 
						math.floor((self.area_factor * 6 + self.area_factor * 1) * 100)) / 100
	
	def place_mountains(self, hex_map):
		for mountain in self.mountains:
			mountain.place_points(hex_map)
	
	def __closest_mountain_distance(self, point):
		min_distance = 5000000
		for mountain in self.mountains:
			distance = mountain.distance(point)
			if distance < min_distance:
				min_distance = distance
		return min_distance
	
	def plot_mountains(self, override=plt):
		for mountain in self.mountains:
			mountain.plot(override=override)