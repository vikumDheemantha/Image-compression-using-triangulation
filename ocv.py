import numpy as np
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('sample.jpg')
e1 = cv2.getTickCount()
# print(cv2.__version__)
# print(img)
# img[150,100] = [255,255,255]
# cv2.namedWindow('Sample', cv2.WINDOW_NORMAL)
# cv2.imshow('Sample', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


print(img.shape)

# Drowings
cv2.line(img,(0,0), (512, 512),(0,0,255), 1)

pts = np.array([[60,75],[200,400],[300,300]], np.int32)
pts2 = np.array([[500,500],[200,400],[300,300]], np.int32)
pts = pts.reshape((-1,1,2))
pts2 = pts2.reshape((-1,1,2))
cv2.polylines(img,[pts, pts2],True,(0,255,255))

b,g,r = cv2.split(img)
# print(img[0,0])
# print('b:', b)
img2 = cv2.merge([r,g,b])
# plt.subplot(121)
# plt.imshow(img) # expects distorted color
# plt.subplot(121)
# plt.imshow(img2) # expect true color
# plt.subplot(121)
# plt.imshow(b) # expect true color
# plt.subplot(122)
# plt.imshow(g) # expect true color
# plt.subplot(12)
# plt.imshow(r) # expect true color
plt.imshow(img2) # expects distorted color
e2 = cv2.getTickCount()
t = (e2 - e1)/cv2.getTickFrequency()
print('count:', t)
plt.show()

# cv2.imshow('bgr image',img) # expects true color
# cv2.imshow('rgb image',img2) # expects distorted color
# cv2.waitKey(0)
# cv2.destroyAllWindows()