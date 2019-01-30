import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('sample.jpg', 0)
print("testing gray:", img[5,5])
imgOriginal = img.copy
size = img.shape
print("Size: ", size)
rect = (0, 0, size[1], size[0])
subdiv  = cv2.Subdiv2D(rect)
# Set the points
points = []
x = 0
while(x<256):
	y = 0
	while(y<256):
		points.append((x, y))
		y = y + 17
	# points.append((x, y-1))
	x = x + 17
# points.append((x, y))

# print(points)
# add points to subdiv
subdiv.insert(points)
triangles = subdiv.getTriangleList()
count = 0
# print()

#teturn the sign
def sign(x1, y1, x2, y2, x3, y3):
	return ((x1-x3)*(y2-y3) - (x2-x3)*(y1-y3))

# check whether given point is inside the triangle or not
# def isInTriangle():
# 	pass
x1 = int(triangles[100, 0])
y1 = int(triangles[100, 1])
x2 = int(triangles[100, 2])
y2 = int(triangles[100, 3])
x3 = int(triangles[100, 4])
y3 = int(triangles[100, 5])

xmin = min(x1, x2, x3)
xmax = max(x1, x2, x3)
ymin = min(y1, y2, y3)
ymax = max(y1, y2, y3)
print("Region", xmin, xmax, ymax, ymin)
for i in range(xmin, xmax+1):
	# print("Range", i)
	for j in range(ymin, ymax+1):
		# img[i, j] = 0
		b1 = sign(i,j, x1, y1, x2, y2)<0
		b2 = sign(i,j, x2, y2, x3, y3)<0
		b3 = sign(i,j, x3, y3, x1, y1)<0

		if((b1 == b2) and (b2 == b3)):
			img[i, j] = 255
			
# Check if a point is inside a rectangle
def rect_contains(rect, point) :
	if point[0] < rect[0] :
		return False
	elif point[1] < rect[1] :
		return False
	elif point[0] > rect[2] :
		return False
	elif point[1] > rect[3] :
		return False
	return True
 
# Draw a point
def draw_point(img, p, color ) :
	cv2.circle( img, p, 2, color)
# Drow delaunay triangle
def draw_delaunay(img, subdiv, delaunay_color ) :
 
	triangleList = subdiv.getTriangleList();
	print("Triangle list: ", triangleList.size)
	size = img.shape
	r = (0, 0, size[1], size[0])
 
	for t in triangleList :
		
		pt1 = (t[0], t[1])
		pt2 = (t[2], t[3])
		pt3 = (t[4], t[5])
		 
		if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3) :
			cv2.line(img, pt1, pt2, delaunay_color)
			cv2.line(img, pt2, pt3, delaunay_color)
			cv2.line(img, pt3, pt1, delaunay_color)

# Define colors for drawing.
delaunay_color = (255,255,255)
points_color = (0, 0, 255)
# Draw delaunay triangles
draw_delaunay( img, subdiv, (255, 255, 255) );
 
# Draw points
# for p in points :
#     draw_point(img, p, (0,0,255))
print("final size", rect)

cv2.imshow('Sample', img)
cv2.waitKey(0)
cv2.destroyAllWindows()