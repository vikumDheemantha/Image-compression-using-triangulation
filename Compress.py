import cv2
import numpy as np
import time
import sys
from tqdm import tqdm

def sign( p1, p2, p3):
	return ((p1[0]-p3[0])*(p2[1]-p3[1]) - (p2[0]-p3[0])*(p1[1]-p3[1]))

def isInTriangle( pt, p1, p2, p3):

	b1 = sign(pt, p1, p2)<0
	b2 = sign(pt, p2, p3)<0
	b3 = sign(pt, p3, p1)<0

	return ((b1 == b2) and (b2 == b3))

def isInTriangle2( pt, p1, p2, p3):

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
def draw_point( img, p, color ) :
	cv2.circle( img, p, 2, color)
# Drow delaunay triangle
def draw_delaunay( img, subdiv, delaunay_color ) :

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

def mean( img, p1, p2, p3):
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
				# print("("+str(i)+","+str(j)+")")
				total = total + img[i, j]
				count = count+1
	if(count != 0):
		return total/count
	else:
		return -1

def isHomogenious( img, p1, p2, p3, rng):
	pixCount = 0
	isHG = True
	m = mean(img, p1, p2, p3)
	# print("mean: ", m)
	if(m != -1):

		xmin = int(min(p1[0], p2[0], p3[0]))
		xmax = int(max(p1[0], p2[0], p3[0]))
		ymin = int(min(p1[1], p2[1], p3[1]))
		ymax = int(max(p1[1], p2[1], p3[1]))

		for i in range(xmin, xmax+1):
			# print("Range", i)
			for j in range(ymin, ymax+1):
				pt = (i, j)
				if(isInTriangle2(pt, p1, p2, p3)):
					pixCount=pixCount+1
					vari = img[i, j] - m
					if(vari<0): vari = vari*(-1)
					if(vari> rng):
						isHG = False
		if(pixCount<=10):
			isHG = True
		return [isHG, m]
	else:
		return [isHG, m]

# genarate new Image
def decodeImage( encImg, size):
	blank_image = np.zeros((size[0],size[1]), np.uint8)
	print("Image is decoding, Please wait: ")
	# print(encImg)
	for t in tqdm(encImg):
		pt1 = (t[0], t[1])
		pt2 = (t[2], t[3])
		pt3 = (t[4], t[5])
		m = t[6]
		r = (0, 0, size[0], size[1])
		xmin = int(min(pt1[0], pt2[0], pt3[0]))
		xmax = int(max(pt1[0], pt2[0], pt3[0]))
		ymin = int(min(pt1[1], pt2[1], pt3[1]))
		ymax = int(max(pt1[1], pt2[1], pt3[1]))

		if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3):
			# sys.stdout.write(next(spinner))
			# sys.stdout.flush()
			# # time.sleep(0.1)
			# sys.stdout.write('\b')
			for i in range(xmin, xmax+1):
				# print("Range", i)
				for j in range(ymin, ymax+1):
					pt = (i, j)
					if(isInTriangle(pt, pt1, pt2, pt3)):
						blank_image[i, j] = m
	print("Decode is completed successfully")
	return blank_image

def calculateMSE(I1, I2):
	shape = I1.shape
	m = shape[0]
	n = shape[1]
	ans = 0

	for i in range(0, m):
		for j in range(0, n):
			ans = ans+(I1[i][j]-I2[i][j])**2
	return ans/(m*n)

def encodeImage( img, rng):
	size = img.shape
	rect = (0, 0, size[0], size[1])
	subdiv  = cv2.Subdiv2D(rect)
	#add some random points to the image for generate first delaunay
	#triangle set. After that through this triangles we check the homogenity
	points = []
	x = 0
	while(x<size[0]):
		y = 0
		while(y<size[1]):
			points.append((x, y))
			y = (y + 50)
		points.append((x, size[1]-1))
		x = x + 50

	y = 0	
	while(y<size[1]):
			points.append((size[0]-1, y))
			y = (y + 20)
	points.append((size[0]-1, size[1]-1))

	#insert generated points to the created subdiv to generate triangulation
	subdiv.insert(points)
	isNotConverges = True
	r = (0, 0, size[0], size[1])
	#collect all the homogenious triangle to a list to reduce the redundunce
	#execution of the code
	homogenTriangles = []
	encodedImage = []
	print("Encoding, Please wait. ")

	""" Splitting the triangles in to smaller triangles """
	#check wether all the triangles are homogenious or not
	while(isNotConverges):
		triangleList = subdiv.getTriangleList()
		isNotConverges = False # temparily make False, if not comverges then
		# again make it true in bellow line by checking the condition
		
		#Check every triangle in the triangle list
		#tqdm is just for ilustrate the progress bars for this method
		for t in tqdm(triangleList) :
			pt1 = (t[0], t[1])
			pt2 = (t[2], t[3])
			pt3 = (t[4], t[5])
			#check the triangle is already checked about homogenious or nor
			if t.tolist() not in homogenTriangles: 
				if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3) :

					(isHOG, m) = isHomogenious(img, pt1, pt2, pt3, rng)
					if(not isHOG):

						# add another vertex to the center of the triangle
						newX = (pt1[0] + pt2[0] + pt3[0])/3
						newY = (pt1[1] + pt2[1] + pt3[1])/3
						newPT = (newX, newY)
						# subdiv.insert(newPT)
						subdiv  = cv2.Subdiv2D(rect)
						points.append(newPT)
						subdiv.insert(points)
						isNotConverges = True
					else:
						# if it is homogenious add it to the set of homogenious
						# triangle for avoid rechecking same triangle
						homogenTriangles.append(t.tolist())
						# generate nee Triangle for encoding
						# newT = t.tolist()
						# newT.append(int(m))
						# newTInt = [int(i) for i in newT]
						# encodedImage.append(newTInt)
						# encodedImage.append(newT)
	
	""" Merger Triangle acording to the similarity/Homogenity """
	print("Merging: ")
	# print(homogenTriangles)
	for p in tqdm(points):
		# points.remove(p)
		# if(not((p[0] == r[0] and p[1] ==r[1]) or (p[0] == r[2]-1 and p[1] ==r[1]) or (p[0] == r[0] and p[1] ==r[3]-1) or (p[0] == r[2]-1 and p[1] ==r[3]-1))):
		if(not((p[0] == r[0] and p[1] ==r[1]) or (p[0] == r[2]-1 and p[1] ==r[1]) or (p[0] == r[0] and p[1] ==r[3]-1) or (p[0] == r[2]-1 and p[1] ==r[3]-1))):
			shouldRemove = False
			neighborTriangle = [t for t in homogenTriangles if (p[0] in t and p[1] in t)]
			# print(neighborTriangle)
			newm = 0
			if(len(neighborTriangle) > 1):
				for t in neighborTriangle:
					newm = newm + mean(img, (t[0],t[1]), (t[2],t[3]), (t[4],t[5]))
				for t in neighborTriangle:
					if(mean(img, (t[0],t[1]), (t[2],t[3]), (t[4],t[5])) - newm<rng):
						shouldRemove = True
				if(shouldRemove):
					points.remove(p)
					subdiv  = cv2.Subdiv2D(rect)
					subdiv.insert(points)
					triangleList = subdiv.getTriangleList()
					homogenTriangles = [t.tolist() for t in triangleList if (rect_contains(r,(t[0], t[1])) and rect_contains(r,(t[2], t[3])) and rect_contains(r,(t[4], t[5])))]

	# print(homogenTriangles)
	for t in homogenTriangles:
		t.append(mean(img, (t[0], t[1]), (t[2], t[3]), (t[4], t[5])))
		if((t[0] ==0 and t[1] ==0)or(t[2] ==0 and t[3] ==0)or (t[4] ==0 and t[5] ==0)):
			print(t)
		encodedImage.append(t)




		
	return encodedImage, subdiv