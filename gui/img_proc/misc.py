import cv2
import numpy

def demosaic(input_im):
    img_data = numpy.asarray(input_im, dtype=numpy.uint8)
    gray = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(gray, cv2.COLOR_BAYER_GR2RGB)
    return rgb

def color_correct(input_im):
    new_im = cv2.cvtColor(input_im, cv2.COLOR_BGR2RGB)
    return new_im

