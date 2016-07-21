from timeit import timeit
import cv2

img = cv2.imread('/home/nathan/python/PyDetect/src/client/assets/webcam.jpg')
fast = cv2.FastFeatureDetector()

print timeit('fast.detect(img, None)', setup="from __main__ import img, fast", number=10000)
