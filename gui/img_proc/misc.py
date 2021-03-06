# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import cv2
import numpy

def apply_equalization(image, clip = 2.0, roi = (8,8)): # image needs to be read in as cv2.imread(image, 1)
    '''
    Equalization helps with the visual output by increasing image contrast
    in an adaptive way and improves keypoint detection in low contrast
    scenarios.

    image is array of uint8 type

    clip is of type float
        USAGE ::   value of 1.0 is subtle, value of 4.0 or 5.0 will be harsh

    roi is a tuple containing two ints representing the roi to be operated on
        USAGE ::   should be of form (n, m)
    '''

    clahe = cv2.createCLAHE(clipLimit = clip, tileGridSize = roi)

    Lab = cv2.split(cv2.cvtColor(image, cv2.COLOR_BGR2LAB))
    
    Lab[0] = clahe.apply(Lab[0])

    return cv2.cvtColor(cv2.merge((Lab[0], Lab[1], Lab[2])), cv2.COLOR_LAB2BGR)

def demosaic(input_im):
    '''
    @depricated: Use color_correct instead.
    Originally, we had Econ Cameras, they were not demosaiced and they put 
    a heavy strain on the tk1, so we demosaiced on clientside
    '''
    img_data = numpy.asarray(input_im, dtype=numpy.uint8)
    gray = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(gray, cv2.COLOR_BAYER_GR2RGB)
    return rgb

def color_correct(input_im):
    '''
    Flip color space for Tkinter
    '''
    b,g,r = cv2.split(input_im)
    img = cv2.merge((r,g,b))
    return img

def mirror_vertical(input_im):
    '''
    Will mirror the image (for cameras that are oriented upside down)
    '''
    return cv2.flip(input_im, 0)
