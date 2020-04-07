import math
import matplotlib.pyplot as plt
import shapely
from region import Region, RegionSet
from plot import plot_pixel, real_to_map
from PIL import Image, ImageDraw
from mountain import Mountain
from hexMap import HexMap

size_x = 4200
size_y = 4200
scale_factor = 20

r = RegionSet()
m = HexMap(r, (size_x, size_y), scale_factor)
for i in range(0, 15):
	region = Region(r)
	region.expand(rounds=5)

image = Image.new("RGB", (int(4200 / scale_factor) + 1, int(4200 / scale_factor) + 1))
draw = ImageDraw.Draw(image)

r.identify_neighbors()
r.complete_intersections()
r.calculate_intersection_areas()
r.plot(override=plt)
r.create_mountain_ranges()
plt.axis((-size_x / 2, size_x / 2, -size_y / 2, size_y / 2))

m.rasterize()
# m.create_image("map.png")
m.save_egg("map.egg", 9)

plt.savefig("graph.png")

# image.show()
# plt.show()