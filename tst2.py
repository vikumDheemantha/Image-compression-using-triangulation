import sys
import time

dictionary = {}

x = (0,1)
y = (1,5)

dictionary[x] = "hello"
dictionary[y] = "world"

print(dictionary.get(y))