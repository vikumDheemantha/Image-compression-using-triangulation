import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import argparse
import pickle
import sys
import itertools

start = time.time()
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input")
parser.add_argument("-o", "--output")
parser.add_argument("-r", "--rng", type=int)
args = parser.parse_args()

def spinning_cursor():
	while True:
		for cursor in '|/-\\':
			yield cursor

spinner = spinning_cursor()

#function to return the sign
def sign(p1, p2, p3):
	return ((p1[0]-p3[0])*(p2[1]-p3[1]) - (p2[0]-p3[0])*(p1[1]-p3[1]))

def isInTriangle(pt, p1, p2, p3):

	b1 = sign(pt, p1, p2)<0
	b2 = sign(pt, p2, p3)<0
	b3 = sign(pt, p3, p1)<0

	return ((b1 == b2) and (b2 == b3))

def isInTriangle2(pt, p1, p2, p3):

	b1 = sign(pt, p1, p2)<=0
	b2 = sign(pt, p2, p3)<=0
	b3 = sign(pt, p3, p1)<=0

	return ((b1 == b2) and (b2 == b3))

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
	size = img.shape
	r = (0, 0, size[1], size[0])
 
	for t in triangleList :
		
		pt1 = (t[1], t[0])
		pt2 = (t[3], t[2])
		pt3 = (t[5], t[4])
		 
		if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3) :
			cv2.line(img, pt1, pt2, delaunay_color)
			cv2.line(img, pt2, pt3, delaunay_color)
			cv2.line(img, pt3, pt1, delaunay_color)

def mean(img, p1, p2, p3):
	total = 0
	count = 0

	x1 = int(p1[0])
	y1 = int(p1[1])
	x2 = int(p2[0])
	y2 = int(p2[1])
	x3 = int(p3[0])
	y3 = int(p3[1])


	xmin = min(x1, x2, x3)
	xmax = max(x1, x2, x3)
	ymin = min(y1, y2, y3)
	ymax = max(y1, y2, y3)

	for i in range(xmin, xmax+1):
		# print("Range", i)
		for j in range(ymin, ymax+1):
			pt = (i, j)
			if(isInTriangle(pt, p1, p2, p3)):
				total = total + img[i, j]
				count = count+1
	if(count != 0):
		return total/count
	else:
		return -1

def isHomogenious(img, p1, p2, p3):
	global args
	isHG = True
	m = mean(img, p1, p2, p3)
	# print("mean: ", m)
	if(m != -1):
		# iMax = m+args.rng
		# iMin = m-args.rng
		# if(iMax>255):iMax = 255
		# if(iMin<0): iMin = 0

		xmin = int(min(p1[0], p2[0], p3[0]))
		xmax = int(max(p1[0], p2[0], p3[0]))
		ymin = int(min(p1[1], p2[1], p3[1]))
		ymax = int(max(p1[1], p2[1], p3[1]))

		for i in range(xmin, xmax+1):
			# print("Range", i)
			for j in range(ymin, ymax+1):
				pt = (i, j)
				if(isInTriangle2(pt, p1, p2, p3)):
					vari = img[i, j] - m
					if(vari<0): vari = vari*(-1)
					if(vari> args.rng):
						isHG = False
		return [isHG, m]
	else:
		return [isHG, m]

# genarate new Image
def decodeImage(encImg):
	blank_image = np.zeros((256,256), np.uint8)
	for t in encImg:
		pt1 = (t[0], t[1])
		pt2 = (t[2], t[3])
		pt3 = (t[4], t[5])
		m = t[6]
		r = (0, 0, 256, 256)
		xmin = int(min(pt1[0], pt2[0], pt3[0]))
		xmax = int(max(pt1[0], pt2[0], pt3[0]))
		ymin = int(min(pt1[1], pt2[1], pt3[1]))
		ymax = int(max(pt1[1], pt2[1], pt3[1]))
		
		if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3):
			print('*', end=' ', flush=True)
			for i in range(xmin, xmax+1):
			# print("Range", i)
				for j in range(ymin, ymax+1):
					pt = (i, j)
					if(isInTriangle(pt, pt1, pt2, pt3)):
						blank_image[i, j] = m
	return blank_image


##### Main Coding #####

img = cv2.imread(args.input, 0)
imgOriginal = img.copy
size = img.shape
rect = (0, 0, size[1], size[0])
subdiv  = cv2.Subdiv2D(rect)

# Initiate the point aray the points
points = []
x = 0
while(x<256):
	y = 0
	while(y<256):
		points.append((x, y))
		y = y + 17
	x = x + 17

subdiv.insert(points)

isNotConverges = True
	# print("Triangle list: ", triangleList.size)
size = img.shape
r = (0, 0, size[1], size[0])
homogenTriangles = []
newImgArray = []
while(isNotConverges):
	triangleList = subdiv.getTriangleList();
	# print("\b", end="")
	# print(pending[pendCount%4], end="")
	print("\n\n-----Still not convergence --------------\n")
	print("Waitting: ", end="", flush=True)
	isNotConverges = False
	for t in triangleList :
		# pt1 = (t[1], t[0])
		# pt2 = (t[2], t[2])
		# pt3 = (t[4], t[5])
		pt1 = (t[0], t[1])
		pt2 = (t[2], t[3])
		pt3 = (t[4], t[5])
		if t.tolist() not in homogenTriangles: 
			if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3) :
				# print("Checking homogenity...")
				
				# print('.', end=' ', flush=True)

				sys.stdout.write(next(spinner))
				sys.stdout.flush()
				# time.sleep(0.1)
				sys.stdout.write('\b')



				(isHOG, m) = isHomogenious(img, pt1, pt2, pt3)
				if(not isHOG):
					newX = (pt1[0] + pt2[0] + pt3[0])/3
					newY = (pt1[1] + pt2[1] + pt3[1])/3
					newPT = (newX, newY)
					subdiv.insert(newPT)
					isNotConverges = True
				else:
					homogenTriangles.append(t.tolist())
					newT = t.tolist()
					newT.append(m)
					newTInt = [int(i) for i in newT]
					newImgArray.append(newTInt)
	# print(homogenTriangles)

draw_delaunay( img, subdiv, (0, 0, 256) );
 
# Draw points
# for p in points :
#     draw_point(img, p, (0,0,255))
# print("final size", rect)
newImg = decodeImage(newImgArray)
print(newImgArray)
now = time.time() - start
print("\n Triangle list: ", triangleList.size)
print("time: ", int(now/60),":", int(now%60))
print("size of original image", sys.getsizeof(img))
print("size of the decoded", sys.getsizeof(newImgArray))
cv2. imwrite("test result/"+args.output+"_Triangle.png", img)
cv2. imwrite("test result/"+args.output+"_decoded.png", newImg)
filename = "test result/"+args.output+"_encoded"
outfile = open(filename,'wb')
pickle.dump(newImgArray,outfile)
outfile.close()

# cv2.imshow('Sample', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
# plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
# plt.show()