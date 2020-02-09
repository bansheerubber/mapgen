import math
from PIL import Image

class HexMap:
	def __init__(self, region_set, world_size, reduction_factor):
		self.hexes = {}
		self.region_set = region_set
		self.world_size = world_size
		self.reduction_factor = reduction_factor # how much we scale the world space down by

		self.color_table = {
			0: (3, 169, 252),
			1: (47, 138, 62),
			2: (112, 112, 112),
		}

	def convert_coord(self, x, y):
		return (math.floor((x + self.world_size[0] / 2) / self.reduction_factor), math.floor((self.world_size[1] / 2 - y) / self.reduction_factor))
	
	def set_hex(self, point, id):
		self.hexes[point] = id

	def rasterize(self):
		placed_ranges = []
		print("rasterizing...")
		for region in self.region_set.regions:
			print(f"rasterizing region {region.index}")
			for point in region.step_area(math.floor(self.reduction_factor / 2)):
				self.hexes[self.convert_coord(point.x, point.y)] = 1
			
		# for region in self.region_set.regions:
			print(f"rasterizing mountains for region {region.index}...")
			for mountain_range in region.mountain_ranges.values():
				if mountain_range not in placed_ranges:
					mountain_range.place_mountains(self)
					placed_ranges.append(mountain_range)
	
	def create_image(self, filename):
		self.image = Image.new("RGB", (int(self.world_size[0] / self.reduction_factor) + 1, int(self.world_size[1] / self.reduction_factor) + 1))
		for x in range(0, math.floor(self.world_size[1] / self.reduction_factor)):
			for y in range(0, math.floor(self.world_size[1] / self.reduction_factor)):
				coord = (x, y)
				hex_id = 0
				if coord in self.hexes:
					hex_id = self.hexes[coord]
				self.image.putpixel(coord, self.color_table[hex_id])
		self.image.show()
		self.image.save(filename)

	def save_egg(self, filename):
		file = open(filename, "wb")
		# writing map size to file
		file.write(bytes([10]))
		file.write(math.floor(self.world_size[0] / self.reduction_factor).to_bytes(4, "big"))
		file.write(math.floor(self.world_size[1] / self.reduction_factor).to_bytes(4, "big"))
		for y in range(0, math.floor(self.world_size[1] / self.reduction_factor)):
			for x in range(0, math.floor(self.world_size[1] / self.reduction_factor)):
				coord = (x, y)
				hex_id = 0
				if coord in self.hexes:
					hex_id = self.hexes[(x, y)]
				file.write(bytes([hex_id]))
		file.close()