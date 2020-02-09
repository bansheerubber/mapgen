import noise
import math
import numpy
import random
from shapely import geometry

class Circle:
	def __init__(self, radius, offset):
		self.points = []
		self.perimeter = []
		self.normals = {}

		self.offset = offset
		self.radius = radius

		resolution = 0.5
		for angle in range(0, math.floor(360 * resolution)):
			richard = angle / resolution * math.pi / 180
			self.points.append((math.floor(math.cos(richard) * radius[0] + offset[0]), math.floor(math.sin(richard) * radius[1] + offset[1])))
		
		# search for a perimeter
		for point in self.points:
			x = point[0]
			y = point[1]
			
			point1 = (x + 1, y)
			point2 = (x - 1, y)
			point3 = (x, y + 1)
			point4 = (x, y - 1)

			if point1 not in self.points \
				or point2 not in self.points \
				or point3 not in self.points \
				or point4 not in self.points:
				self.perimeter.append(point)
				# calculate the normal
				local_x = x - offset[0]
				local_y = y - offset[0]
				angle = math.atan2(local_y, local_x)
				self.normals[point] = (math.cos(angle), math.sin(angle))
	
	def draw_perimeter(self):
		for point in self.perimeter:
			pixel_points[point] = (255, 255, 255)
	
	def expand_perimeter(self):
		base = random.randint(0, 50000)
		std = self.is_interesting(base)
		while std < 0.1:
			base = random.randint(0, 5000)
			std = self.is_interesting(base)

		distance = (self.radius[0] + self.radius[1]) / 2
		for i in range(0, len(self.perimeter)):
			repeat = 5
			mi = i / len(self.perimeter) * repeat
			scale = noise.pnoise1(mi, 2, repeat=repeat, base=base) * 100 * distance / 150

			point = self.perimeter[i]
			normal = self.normals[point]
			self.perimeter[i] = (math.floor(point[0] + normal[0] * scale), math.floor(point[1] + normal[1] * scale))

	def is_interesting(self, base):
		array = []
		for i in range(0, 50):
			repeat = 5
			mi = i / 50 * repeat
			scale = noise.pnoise1(mi, 2, repeat=repeat, base=base, lacunarity=(len(self.perimeter) / 1000 + 1))
			array.append(scale)
		return numpy.std(array)
	
	def to_shapely(self):
		return geometry.Polygon([p[0], p[1]] for p in self.perimeter)