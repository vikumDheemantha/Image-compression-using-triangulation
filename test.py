import cv2
import numpy as np
import Compress as Com
import argparse
import sys
import pickle

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input")
parser.add_argument("-o", "--output")
parser.add_argument("-r", "--rng", type=int)
args = parser.parse_args()

img = cv2.imread(args.input, 0)
imgOriginal = img
size = img.shape

compressedImage, subDiv = Com.encodeImage(img, args.rng)

Com.draw_delaunay(img, subDiv, (0, 0, 256))
newImg = Com.decodeImage(compressedImage, size)

print("size of original image: ", sys.getsizeof(img))
print("size of the decoded: ", sys.getsizeof(compressedImage))

cv2. imwrite("test result/"+args.output+"_Triangle.png", img)
cv2. imwrite("test result/"+args.output+"_decoded.png", newImg)

filename = "test result/"+args.output+"_encoded"
outfile = open(filename,'wb')
pickle.dump(compressedImage,outfile)
outfile.close()

filename = "test result/"+args.output+"_info.txt"
textOut= open(filename,"w+")

textOut.write("Size of original image: "+str(sys.getsizeof(img)) + "\n")
textOut.write("Size of decoded image: "+str(sys.getsizeof(compressedImage)) + "\n")
textOut.close()
