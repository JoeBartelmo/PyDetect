import cv2


v = cv2.VideoCapture(1)
img = None

try:
    while True:
        flag, frame = v.read()
        if not flag : break

        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        img = cv2.cvtColor(gray, cv2.COLOR_BAYER_GR2RGB)
        cv2.imshow('', img)
        cv2.waitKey(1)

except KeyboardInterrupt:
    pass

cv2.imwrite('ideal_image1.jpg', img)

