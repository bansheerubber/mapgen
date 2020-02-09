import matplotlib.pyplot as plt
import math
import random

class Mountain:
	def __init__(self, position, radius, index):
		self.position = position
		self.radius = radius
		self.index = index

	def plot(self, override=plt):
		override.gca().add_artist(override.Circle(self.position, self.radius, color=(1, 0, 0)))
	
	def distance(self, mountain_or_point):
		if isinstance(mountain_or_point, Mountain):
			mountain = mountain_or_point
			return math.sqrt((self.position[0] - mountain.position[0]) ** 2 + (self.position[1] - mountain.position[1]) ** 2)
		else:
			point = mountain_or_point
			return math.sqrt((self.position[0] - point[0]) ** 2 + (self.position[1] - point[1]) ** 2)
	
	def place_points(self, hex_map):
		for degrees in range(0, 360, hex_map.reduction_factor * 2):
			for radius in range(math.floor(self.radius / 4), math.ceil(self.radius)):
				angle = degrees * math.pi / 180
				coord = (math.cos(angle) * radius + self.position[0], math.sin(angle) * radius + self.position[1])
				if random.randint(0, 5) == 2:
					hex_map.set_hex(hex_map.convert_coord(coord[0], coord[1]), 2)