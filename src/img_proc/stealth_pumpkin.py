import block
import numpy
import cv2
import highlight
import math

def stealth_pumpkin(img, img_keypoints, block_size=8):
    
    counts = numpy.zeros((img.shape[0:2]))
    r = block_size / 2

    for kp in img_keypoints:
        col, row = kp.pt

        counts[row-r:row+r, col-r:col+r] += 1

    return counts
    
def sneaky_squash(ideal_counts, frame_counts, threshold=5):
    delta = numpy.absolute(ideal_counts - frame_counts)
    #print delta.shape
    return delta>=threshold

def script(in_q, out_q1, ideal_image_file):
    # load ideal image
    ideal_image = cv2.imread(ideal_image_file)

    fast = cv2.FastFeatureDetector()

    ideal_image_kp = fast.detect(ideal_image, None)
    pump = stealth_pumpkin(ideal_image, ideal_image_kp)

    while True:
        q_image = in_q.get()

        if type(q_image) is not numpy.ndarray or q_image is None:
            print 'wrong type'
            continue
 
        q_image_kp = fast.detect(q_image, None)
        squash = stealth_pumpkin(q_image, q_image_kp)

        pumpkins_indexes = sneaky_squash(pump, squash)

        out_image = highlight.highlight(q_image, pumpkins_indexes, color=(255,0,0))
        out_q1.put(out_image)

def demosaic(input_im):
    gray = cv2.cvtColor(input_im, cv2.COLOR_RGB2GRAY)
    img = cv2.cvtColor(gray, cv2.COLOR_BAYER_GR2RGB)
    return img

if __name__=='__main__':
    v = cv2.VideoCapture(1)
    fast = cv2.FastFeatureDetector()

    f, ideal_image = v.read()
    fast = cv2.FastFeatureDetector()

    ideal_image_kp = fast.detect(ideal_image, None)
    pump = stealth_pumpkin(ideal_image, ideal_image_kp)

    cv2.imshow('ideal', ideal_image)
    cv2.waitKey(1)

    while True:
        f, q_image = v.read()

        if type(q_image) is not numpy.ndarray or q_image is None:
            print 'wrong type'
            continue
 
        q_image_kp = fast.detect(q_image, None)
        squash = stealth_pumpkin(q_image, q_image_kp)

        pumpkins_indexes = sneaky_squash(pump, squash)

        out_image = highlight.highlight(q_image, pumpkins_indexes, color=(255,0,0))
        
        cv2.imshow('live', out_image)
        cv2.waitKey(1)
