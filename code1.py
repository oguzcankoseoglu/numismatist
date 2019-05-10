import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from picamera import PiCamera
from datetime import datetime
import RPi.GPIO as GPIO
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.setup(22, GPIO.IN)

GPIO.setup(18, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

def start():
    camera = PiCamera()
    camera.start_preview()
    time.sleep(8)
    now = datetime.fromtimestamp(time.time()).strftime("%d-%m-%Y_%H.%M.%S")
    camera.capture('/home/pi/Desktop/numismatist/static/image' + now + '.png')
    camera.stop_preview()
    camera.close()

    image = cv2.imread('/home/pi/Desktop/numismatist/static/image' + now + '.png')
    output = image.copy()

    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #cv2.imshow("gray", gray)

    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    #cv2.imshow("Blurred", gray)

    gray = cv2.medianBlur(gray,5)

    edged = cv2.Canny(gray, 50, 200, 10)
    #cv2.imshow("Canny", edged)


    gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,3.5)
    #cv2.imshow("Threshed", gray)


    kernel = np.ones((1,2,1,5),np.uint8)
    gray = cv2.erode(gray,kernel,iterations = 1)


    # detect circles in the image
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 45, param1=75,
                                                            param2=40,
                                                            minRadius=20,
                                                            maxRadius=90)

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        x=0
        y=0
        r=0
        coin_number = 0
        total_number = []
        radius_of_circles = []
        filename = ""
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            coin_number += 1
            total_number.append(coin_number)
            coin_str = str(coin_number)
            print ('Coin number:' + coin_str)
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            print ("Column Number: ")
            print (y)
            print ("Row Number: ")
            print (x)
            print ("Radius is: ")
            print (r)
            radius_of_circles.append(str(r))

        print('Number of Coins: ' + str(coin_number))
        print('Total coins: ' + str(total_number))
        #plt.plot(total_number, radius_of_circles, 'ro')
        # naming the x axis
        #plt.xlabel('number of coin')
        # naming the y axis
        #plt.ylabel('radius')
        # function to show the plot
        #plt.show()

        # show the output image
        path = "/home/pi/Desktop/numismatist/static/"
        cv2.imwrite(os.path.join(path, "output" + now + ".png"), np.hstack([output]))
        filename = path + "output" + now + ".png"
        result = [str(coin_number), radius_of_circles, filename]
        return result
    else:
        result = ["No coins detected! There might be a unidentified object!", None, None]
        #GPIO.output(18, True)
        return result
