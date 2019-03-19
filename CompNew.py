import numbers

import cv2
import numpy as np
import time
import sys
from tqdm import tqdm


def sign(p1, p2, p3):
    """
    Function for check which side p1 according to the line p2-p3
    Args:
        p1(tuple): That contain x coordinate and y coordinate
        p2:
        p3:

    Returns:
        bool: true if p1 lies left side of the p2-p3 line, false otherwise

    """
    
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def isInTriangle(pt, p1, p2, p3):
    '''
    Check whether given vertex pt lies inside the triangle(p1-p2-p3) or not
    Args:
        pt(tuple): vertex that need to check with the triangle vertices
        p1(tuple): Triangle vertex
        p2(tuple): Triangle vertex
        p3(tuple): Triangle vertex

    Returns:
        Returns True if pt is inside the triangle, otherwise return False

    '''
    b1 = sign(pt, p1, p2) < 0
    b2 = sign(pt, p2, p3) < 0
    b3 = sign(pt, p3, p1) < 0

    return (b1 == b2) and (b2 == b3)


def isInTriangle2(pt, p1, p2, p3):
    '''
    Check whether given vertex pt lies inside the triangle(p1-p2-p3) or not
    Args:
        pt(tuple): vertex that need to check with the triangle vertices
        p1(tuple): Triangle vertex
        p2(tuple): Triangle vertex
        p3(tuple): Triangle vertex

    Returns:
        Returns True if pt is inside the triangle, otherwise return False

    '''
    b1 = sign(pt, p1, p2) <= 0
    b2 = sign(pt, p2, p3) <= 0
    b3 = sign(pt, p3, p1) <= 0

    return (b1 == b2) and (b2 == b3)


def rect_contains(rect, point):
    '''
    check wether given point is inside the rectangle or note
    Args:
        rect(tuple): rectangle that want to check the given point is inside in it or not
        point(tuple): vertex that want to check with rectangle

    Returns: if point is inside the rectangle then True, otherwise False

    '''
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] >= rect[2]:
        return False
    elif point[1] >= rect[3]:
        return False
    return True


# Draw a point
def draw_point(img, p, color):
    cv2.circle(img, p, 2, color)


# Draw Delaunay triangle
def draw_delaunay(img, subdiv, delaunay_color):
    triangle_list = subdiv.getTriangleList()
    size = img.shape
    r = (0, 0, size[1], size[0])

    for t in triangle_list:

        pt1 = (t[1], t[0])
        pt2 = (t[3], t[2])
        pt3 = (t[5], t[4])

        if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3):
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

    for i in range(xmin, xmax + 1):
        # print("Range", i)
        for j in range(ymin, ymax + 1):
            pt = (i, j)
            if isInTriangle(pt, p1, p2, p3):
                total = total + img[i, j]
                count = count + 1
    if count != 0:
        return total / count
    else:
        return -1


def isHomogeneous(img, p1, p2, p3, rng):
    pixCount = 0
    isHG = True
    m = mean(img, p1, p2, p3)
    # print("mean: ", m)
    if m != -1:

        xmin = int(min(p1[0], p2[0], p3[0]))
        xmax = int(max(p1[0], p2[0], p3[0]))
        ymin = int(min(p1[1], p2[1], p3[1]))
        ymax = int(max(p1[1], p2[1], p3[1]))

        for i in range(xmin, xmax + 1):
            # print("Range", i)
            for j in range(ymin, ymax + 1):
                pt = (i, j)
                if isInTriangle2(pt, p1, p2, p3):
                    pixCount = pixCount + 1
                    vari = img[i, j] - m
                    if vari < 0:
                        vari = vari * (-1)
                    if vari > rng:
                        isHG = False
        if pixCount <= 5:
            isHG = True
        return [isHG, m]
    else:
        return [isHG, m]


# genarate new Image

def decodeImage(enc_img, size):
    blank_image = np.zeros((size[0], size[1]), np.uint8)
    filename = "info.txt"
    # txt = open(filename, "w+")
    # Subdiv for generate delaunay
    rect = (0, 0, size[0], size[1])
    subdiv = cv2.Subdiv2D(rect)
    imgDictionary = {}

    # txt.write("==========points =================== \n")
    print("Image is decoding, Please wait: ")
    points = []
    for t in tqdm(enc_img):
        x = round(t[0], 5)
        y = round(t[1], 5)
        # print(str(x)+"," + str(y))
        color = t[2]
        imgDictionary[(x,y)] = color
        points.append((x, y))
        blank_image[int(round(x)), int(round(y))] = color

        # txt.write(str(x) + ", " + str(y) + "\n")

    # txt.write("==================================== \n")
    # Add point to subdev and taking the list of triangle
    subdiv.insert(points)
    triangleList = subdiv.getTriangleList()
    # txt.write("===============Triangle generated by ===================== \n")
    for t in triangleList:
        p1 = (t[0], t[1])
        p2 = (t[2], t[3])
        p3 = (t[4], t[5])


        # check wether the vertexes in the triangle is in the image range
        if rect_contains(rect, p1) and rect_contains(rect, p2) and rect_contains(rect, p3):
            print(p1, end= ",")
            print(p2, end=",")
            print(p3)
            # txt.write(str(p1) + ", " + str(p2) + ", " + str(p3) + "\n")
            xmin = int(min(p1[0], p2[0], p3[0]))
            xmax = int(max(p1[0], p2[0], p3[0]))
            ymin = int(min(p1[1], p2[1], p3[1]))
            ymax = int(max(p1[1], p2[1], p3[1]))

            for i in range(xmin, xmax + 1):
                for j in range(ymin, ymax + 1):
                    pt = (i, j)
                    if (isInTriangle(pt, p1, p2, p3) and (
                            (p2[1] - p3[1]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[0] - p3[1])) != 0):
                        # w1, w2, w3 are the weights of the p1, p2, p3 respectively
                        w1 = ((p2[1] - p3[1]) * (i - p3[0]) + (p3[0] - p2[0]) * (j - p3[1])) / (
                                (p2[1] - p3[1]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[0] - p3[1]))
                        w2 = ((p3[1] - p1[1]) * (i - p3[0]) + (p1[0] - p3[0]) * (j - p3[1])) / (
                                (p2[1] - p3[1]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[0] - p3[1]))
                        w3 = 1 - w1 - w2
                        # color = int(round((w1 * blank_image[p1[0], p1[1]]) + (w2 * blank_image[p2[0], p2[1]]) + (
                        #         w3 * blank_image[p3[0], p3[1]])))

                        color = int(round((w1 * imgDictionary.get(p1)) + (w2 * imgDictionary.get(p2)) + (
                                w3 * imgDictionary.get(p3))))
                        blank_image[i, j] = color

    print("Decode is completed successfully")
    # txt.close()
    return blank_image


def calculateMSE(I1, I2):
    shape = I1.shape
    m = shape[0]
    n = shape[1]
    ans = 0

    for i in range(0, m):
        for j in range(0, n):
            ans = ans + (I1[i][j] - I2[i][j]) ** 2
    return ans / (m * n)


def encodeImage(img, rng):
    '''Function for encode image



    Args:
        img: image that read from the openCV imread() function or alternative function that give similar kind of object
        rng (int): range that use to threshold the triangle for homogeneous check

    Returns:
        (encodedImage, subdiv): encoded image and subdiv for draw the triangulation

    '''
    size = img.shape
    rect = (0, 0, size[0], size[1])
    subdiv = cv2.Subdiv2D(rect)
    # add some random points to the image for generate first delaunay
    # triangle set. After that through this triangles we check the homogeneity
    points = []
    x = 0
    while x < size[0]:
        y = 0
        while y < size[1]:
            points.append((x, y))
            y = (y + 50)
        points.append((x, size[1] - 1))
        x = x + 50

    y = 0
    while y < size[1]:
        points.append((size[0] - 1, y))
        y = (y + 20)
    points.append((size[0] - 1, size[1] - 1))

    # insert generated points to the created subdiv to generate triangulation
    subdiv.insert(points)
    isNotConverges = True
    r = (0, 0, size[0], size[1])
    # collect all the homogenious triangle to a list to reduce the redundunce
    # execution of the code
    homogenTriangles = []
    encodedImage = []
    print("Encoding, Please wait. ")

    """ Splitting the triangles in to smaller triangles """
    # check wether all the triangles are homogenious or not
    while isNotConverges:
        triangleList = subdiv.getTriangleList()
        isNotConverges = False  # temparily make False, if not comverges then
        # again make it true in bellow line by checking the condition

        # Check every triangle in the triangle list
        # tqdm is just for ilustrate the progress bars for this method
        for t in tqdm(triangleList):
            pt1 = (t[0], t[1])
            pt2 = (t[2], t[3])
            pt3 = (t[4], t[5])
            # check the triangle is already checked about homogenious or nor
            if t.tolist() not in homogenTriangles:
                if rect_contains(r, pt1) and rect_contains(r, pt2) and rect_contains(r, pt3):

                    (isHOG, m) = isHomogeneous(img, pt1, pt2, pt3, rng)
                    if not isHOG:

                        # add another vertex to the center of the triangle
                        # Had to round up the x and y because image can only have integers
                        newX = (pt1[0] + pt2[0] + pt3[0]) / 3
                        newY = (pt1[1] + pt2[1] + pt3[1]) / 3
                        newPT = (newX, newY)
                        # newPT = (newX, newY)
                        # subdiv.insert(newPT)
                        subdiv = cv2.Subdiv2D(rect)
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
    # Assgin color value to each point
    for p in tqdm(points):
        x = p[0]
        y = p[1]
        color = img[int(round(x)), int(round(y))]
        vertex = [x, y, color]
        encodedImage.append(vertex)

    return encodedImage, subdiv
