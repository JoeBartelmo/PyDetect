import numpy
import block
import cv2
import highlight

def rms(imgA, imgB, ax=None):
    """ calculate root mean square between 2 images. """
    # imgA and imgB: 2 or 3d numpy arrays of the same shape
    # axis: 2 or 3 element tuple indicating which axis to calculate the mean across
    # Notes: n/a

    if imgA.shape != imgB.shape:
        raise ValueError('The input images are not the same shape.') 

    rms = ((imgA - imgB) ** 2).mean(axis=ax)
    return rms

def script(in_q, out_q1):
    # load ideal image
    ideal_image = cv2.imread('/home/nathan/python/PyDetect/src/client/assets/webcam.jpg')

    if ideal_image is None:
        return

    block_size = 8
    ideal_image_blocks = block.block_img(ideal_image, x_block_size=block_size, y_block_size=block_size)
    num_block_r = len(range(0, ideal_image.shape[0], block_size))
    num_block_c = len(range(0, ideal_image.shape[1], block_size))

    while True:
        q_image = in_q.get()
        
        whole_img_rms = rms(q_image, ideal_image)

        q_img_blocks = block.block_img(q_image, x_block_size=block_size, y_block_size=block_size)

        rms_img = numpy.zeros((q_image.shape[0:2]))

        for k in range(len(q_img_blocks)):
            if rms(q_img_blocks[k], ideal_image_blocks[k]) > whole_img_rms:
                idx = numpy.unravel_index(k, (num_block_r, num_block_c))
                
                rms_img[idx[0] * block_size: idx[0] * block_size+ block_size, \
                        idx[1] * block_size: idx[1] * block_size+ block_size] = 255
        
        indices = numpy.where(rms_img == 255)

        out_image = highlight.highlight(q_image, indices, color=(0,255,0))
        out_q1.put(out_image)
        

if __name__=='__main__':
    import cv2

    a = cv2.imread('elon_2_copy2.jpg', 0)
    b = cv2.imread('elon_2_finalcopy_unmod.jpg', 0)
    
    a_b_rms = rms(a, b)
    print a_b_rms
    print a.shape

    cv2.namedWindow('bob')

    x = 2
    
    a_blocks = block_img(a, x_block_size=x, y_block_size=x)
    b_blocks = block_img(b, x_block_size=x, y_block_size=x)
    rms_s = []

    for k in range(len(a_blocks)):
        rms_s.append(rms(a_blocks[k], b_blocks[k]))
        
    rms_s = numpy.absolute(numpy.array(rms_s))
    rms_img = ((rms_s / numpy.amax(rms_s)) * 255)
    rms_img = numpy.reshape(rms_img, (a.shape[0] / x + 1, a.shape[1] / x ))
    
    print rms_img.shape
    print rms_img.mean()

    cv2.imshow('bob', rms_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('output.jpg', rms_img)
