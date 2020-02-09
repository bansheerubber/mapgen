import math
from PIL import ImageDraw

def plot_pixel(image, coordinate, color, coord_space, factor, draw=None):
	pixel_coordinate = real_to_map(coordinate[0], coordinate[1], coord_space[0], coord_space[1], factor)
	if pixel_coordinate[0] > coord_space[0] / factor \
		or pixel_coordinate[1] > coord_space[1] / factor \
		or pixel_coordinate[0] < 0 \
		or pixel_coordinate[1] < 0:
		return

	image.putpixel(pixel_coordinate, color)
	return pixel_coordinate

def real_to_map(coord_x, coord_y, coord_space_x, coord_space_y, factor):
	return (math.floor((coord_x + coord_space_x / 2) / factor), math.floor((coord_space_y / 2 - coord_y) / factor))