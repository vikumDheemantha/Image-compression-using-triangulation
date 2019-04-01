import numbers

import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import sys
from tqdm import tqdm


# img = cv2.imread('0266554465.jpeg',0)

def DetectEdge(img):
    """
    Identify the edges in the image using canny operation and make new image with canny operation.

    Args:
        img: image that you want to detect edges

    Returns:
        egges: another image that display white edges in gray background

    """

    edges = cv2.Canny(img, 100, 200)
    return edges


def getEdgePoints(img):
    """
    This method is for return the points that is required to initialize the
    Delaunay triangulation for the image compression method. points are created
    using the DetectEdge() method.

    Args:
        img: image that you need to detect edges

    Returns:
        pointList: list of verteces that draws the edges of the given image

    """
    edges = DetectEdge(img)
    m, n = edges.shape
    pointList = []
    for x in range(0, m):
        for y in range(0, n):
            if edges[x, y] == 255:
                point = (x, y)
                pointList.append(point)
                if (x + 10) <= (m - 1): x = (x + 10)
                if (y + 10) <= (n - 1): y = (y + 10)
    return pointList

# points = getEdgePoints(img)
