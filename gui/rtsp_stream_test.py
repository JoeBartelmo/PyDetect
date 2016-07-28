import cv2

stream = 'rtsp://129.21.56.100:8555/'

vid = cv2.VideoCapture(stream)

while True:
    fl, fr = vid.read()
    if fl:
        cv2.imshow(stream, fr)
        cv2.waitKey(1)

