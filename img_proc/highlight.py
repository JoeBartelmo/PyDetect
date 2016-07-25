import numpy
import cv2

def highlight(img, pixels, color, alpha=0.5):
    """ highlight pixels in image of channel. """
    # img: numpy or opencv 3 channeled image
    # pixels: 2d boolean or index array
    # color: 3 item tuple, indicates color of pixel shadin, ex. (0, 0, 255)
    # alpha: how transparent to make the drawing, 0-1 (1 is opaque)

    overlay = img.copy()
    overlay[pixels] = color
    
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    return img

def script(inq1, inq2, outq):
    # first q is images, second is indices
    color1 = (0, 255, 0)
    color2 = (255, 0, 0)

    while True:
        frame = inq1.get()

        idx_1 = inq2.get()
        idx_2 = inq2.get()

        ret1 = highlight(frame, idx_1, color1, alpha=0.6)
        ret2 = highlight(ret1, idx_2, color2, alpha=0.6)

        outq.put(ret2)

if __name__=='__main__':
    img = cv2.imread('test/elon_2_copy2.jpg',1)

    output = highlight(img, numpy.where(img[:,:,0]>200), (128, 255, 0))

    cv2.namedWindow(' ')
    cv2.imshow(' ', output)
    cv2.waitKey(10000)
    
