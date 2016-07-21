import numpy

def block_img(img, x_block_size=100, y_block_size=100, x_offset=0, y_offset=0):
    """ split image up into evenly sized blocks. """
    # img: a 2 or 3d numpy array of type uint8
    # the rest are self explanatory 
    
    if type(img) is not numpy.ndarray or img is None:
        print 'wrong type'
        return

    blocks = []

    for i in range(x_offset, img.shape[0], x_block_size):
        for j in range(y_offset, img.shape[1], y_block_size):
            blocks.append(img[i:i+x_block_size,j:j+y_block_size])

    return blocks

