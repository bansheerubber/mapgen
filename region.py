from circle import Circle
from mountainRange import MountainRange
import shapely
from shapely.ops import cascaded_union
import shapely
from shapely.wkt import dumps
from shapely.wkt import loads
import random
import math
import matplotlib.pyplot as plt

class RegionSet:
	def __init__(self):
		self.regions = []
	
	def identify_neighbors(self):
		for region in self.regions:
			region.neighbors = [] # reset our neighbors list
		
		for region1 in self.regions:
			for region2 in self.regions:
				if region1 != region2 and region1 not in region2.neighbors and (region2.polygon.intersects(region1.polygon) or region2.polygon.touches(region1.polygon)):
					region2.neighbors.append(region1)
					region1.neighbors.append(region2)
	
	def __clean_regions(self):
		for region in self.regions:
			if region.polygon.is_valid == False:
				region.polygon = region.polygon.buffer(0)

	def complete_intersections(self):
		self.__clean_regions()
		for region in self.regions:
			for neighbor in region.neighbors:
				which = random.randint(0, 1)
				if which == 1:
					region.special_intersect(neighbor)
				else:
					neighbor.special_intersect(region)
				
				# fixing polygons
				if region.polygon.is_valid == False:
					region.polygon = region.polygon.buffer(0)
				
				if neighbor.polygon.is_valid == False:
					neighbor.polygon = neighbor.polygon.buffer(0)
		
		self.identify_neighbors() # we have to reset our neighbors list, so it reflects the actual map
	
	def plot(self, override=plt, alpha=1):
		for region in self.regions:
			region.plot(override=override, alpha=alpha)
	
	def contains_point(self, point):
		point = shapely.geometry.Point(point[0], point[1])
		for region in self.regions:
			if region.polygon.contains(point):
				return True
		return False
	
	def calculate_intersection_areas(self):
		for region in self.regions:
			region.travel()

		for region in self.regions:
			region.calculate_intersection_area()
		
		for region in self.regions:
			region.reverse_travel()
	
	def create_mountain_ranges(self):
		for region in self.regions:
			region.create_mountain_ranges()

TRAVEL_SPEED = 50
# a region represents a sort of biome for map generation. it decides how terrain is formed.
class Region:
	def __init__(self, region_set):
		self.polygon = None # this is how we store the shape of the region
		self.set = region_set

		radius_x = random.randint(50, 400)
		radius_y = random.randint(50, 400)
		
		self.start_circle = Circle((radius_x, radius_y), self.__get_random_position())
		self.start_circle.expand_perimeter()
		self.circles = []

		random_angle = (random.randint(0, 3600) / 10) * math.pi / 180
		self.travel_direction = (math.cos(random_angle), math.sin(random_angle)) # the direction that this region is traveling in, like tectonic plates
		self.travel_speed = random.randint(100, 300) / 100

		self.neighbors = [] # other regions that we intersect with. once we finish generating the regions, these will be our neighbors
		self.neighbor_intersection_area = {} # table for neighbor to its intersection area, after travel
		self.mountain_ranges = {} # the boundaries that we have with our neighbors
		self.complete_intersections = {} # whether or not we have finished a special intersect with a region

		self.polygon = self.start_circle.to_shapely()
		self.set.regions.append(self)
		self.index = self.set.regions.index(self)
		# plt.plot(*self.polygon.exterior.xy)
	
	# gets a random position that we use as our offset
	def __get_random_position(self):
		min_x = -1400
		min_y = -1000

		max_x = 1400
		max_y = 1000

		x = random.randint(min_x, max_x)
		y = random.randint(min_y, max_y)
		while self.set.contains_point((x, y)):
			x = random.randint(min_x, max_x)
			y = random.randint(min_y, max_y)
		return (x, y)

	def plot(self, override=plt, alpha=1):
		if isinstance(self.polygon, shapely.geometry.Polygon):
			override.fill(*self.polygon.exterior.xy, alpha=alpha)
			override.arrow(self.polygon.centroid.x, self.polygon.centroid.y, self.travel_direction[0] * 100 * self.travel_speed, self.travel_direction[1] * 100 * self.travel_speed, head_width=50, head_length=50, facecolor=(0, 0, 0))
			override.text(self.polygon.centroid.x, self.polygon.centroid.y, str(self.index))
	
	def create_mountain_ranges(self, override=plt):
		if isinstance(self.polygon, shapely.geometry.Polygon):
			for neighbor in self.neighbors:
				if isinstance(neighbor.polygon, shapely.geometry.Polygon) and neighbor not in self.mountain_ranges:
					intersection = self.polygon.intersection(neighbor.polygon)
					mountain_range = MountainRange(intersection, self.neighbor_intersection_area[neighbor] / 10000)
					mountain_range.create_mountains()
					mountain_range.plot_mountains(override=plt)
					# mountain_range.plot(mountain_range.intersection, override=override)

					self.mountain_ranges[neighbor] = mountain_range
					neighbor.mountain_ranges[self] = mountain_range
	
	# makes the polygon travel a certain amount
	def travel(self):
		self.old_polygon = self.polygon
		self.polygon = shapely.affinity.translate(self.polygon, \
			xoff=self.travel_direction[0] * TRAVEL_SPEED * self.travel_speed, \
			yoff=self.travel_direction[1] * TRAVEL_SPEED * self.travel_speed)
	
	# reverts polygon back to its original position
	def reverse_travel(self):
		self.polygon = self.old_polygon # reload the old polygon
	
	# goes through all of elements neighbors and figures out the area of the intersection. determines how big mountains should be at the neighbor's respective borders
	def calculate_intersection_area(self):
		for neighbor in self.neighbors:
			if neighbor not in self.neighbor_intersection_area:
				intersection = self.polygon.intersection(neighbor.polygon)
				if isinstance(intersection, shapely.geometry.MultiPolygon):
					intersection = get_largest_polygon(intersection)
				
				self.neighbor_intersection_area[neighbor] = intersection.area
				neighbor.neighbor_intersection_area[self] = intersection.area
	
	def special_intersect(self, region2):
		if region2 not in self.complete_intersections \
			and self not in region2.complete_intersections: # this additional test is redundant, but whatever
			if self.polygon.intersects(region2.polygon) == True:
				self.polygon = (self.polygon.symmetric_difference(region2.polygon)).difference(region2.polygon)
				self.fix_multipolygon()
			
			self.complete_intersections[region2] = True
			region2.complete_intersections[self] = True
	
	def step_area(self, step):
		bounds = self.polygon.bounds
		output = []
		for x in range(math.ceil(bounds[0]), math.floor(bounds[2]), step):
			for y in range(math.ceil(bounds[1]), math.floor(bounds[3]), step):
				output.append(shapely.geometry.Point(x, y))
		intersection = self.polygon.intersection(shapely.geometry.MultiPoint(output))
		if isinstance(intersection, shapely.geometry.Point):
			return []
		else:
			return intersection

	# expands the region outwards in a random direction
	def expand(self, rounds=1):
		for i in range(0, rounds):
			random_angle = random.random() * 360 * math.pi / 180
			random_distance = random.randint(0, 125)
			random_radius_factor = 1.1
			random_radius_range = (50, 250)
			
			radius_x = random.randint(math.floor(random_distance * random_radius_factor + random_radius_range[0]), math.floor(random_distance * random_radius_factor + random_radius_range[1]))
			radius_y = random.randint(math.floor(random_distance * random_radius_factor + random_radius_range[0]), math.floor(random_distance * random_radius_factor + random_radius_range[1]))
			x = math.cos(random_angle) * (self.start_circle.radius[0] + random_distance) + self.start_circle.offset[0]
			y = math.sin(random_angle) * (self.start_circle.radius[1] + random_distance) + self.start_circle.offset[1]
			new_circle = Circle((radius_x, radius_y), (x, y))
			new_circle.expand_perimeter()
			new_polygon = new_circle.to_shapely()

			self.polygon = cascaded_union([self.polygon, new_polygon])
			self.fix_multipolygon()

	def fix_multipolygon(self):
		# if we have a multipolygon, only use the largest polygon in the set
		if isinstance(self.polygon, shapely.geometry.MultiPolygon):
			self.polygon = get_largest_polygon(self.polygon)
		self.polygon = loads(dumps(self.polygon, rounding_precision=0)) # round to integers
			

def get_largest_polygon(multipolygon):
	max_exterior_count = 0
	max_exterior = None
	for polygon in multipolygon:
		if len(polygon.exterior.coords) > max_exterior_count and isinstance(polygon, shapely.geometry.Polygon):
			max_exterior_count = len(polygon.exterior.coords)
			max_exterior = polygon
	return max_exterior