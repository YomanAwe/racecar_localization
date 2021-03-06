#!/usr/bin/env python
import numpy as np
import cv2
import matplotlib.pyplot as plt

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge,  CvBridgeError
import threading


class challengeDetect:
    def __init__(self):
        self.node_name = "Challenge Tracker"
        self.thread_lock = threading.Lock()
        
        self.sub_image = rospy.Subscriber("/camera/rgb/image_rect_color",\
                Image, self.cbImage, queue_size=1)
        self.pub_image = rospy.Publisher("~echo_image",\
                Image, queue_size=1)
        self.pub_notification = rospy.Publisher("/exploring_challenge", String, queue_size=10)
        self.notification = String()

        self.image_count = 0

        self.debugging = debugging

        self.bridge = CvBridge()

        self.image0 = cv2.imread('img/image00.jpg', 0) # sertac
        self.image1 = cv2.imread('img/image01.png', 0) # car
        self.image2 = cv2.imread('img/image02.jpg', 0) # ari
        self.image3 = cv2.imread('img/image03.jpg', 0) # cat
        self.images = [self.image0, self.image1, self.image2, self.image3]
        rospy.loginfo("[%s] Initialized." %(self.node_name))

    def cbImage(self,image_msg):
        thread = threading.Thread(target=self.processImage,args=(image_msg,))
        thread.setDaemon(True)
        thread.start()


    def processImage(self, image_msg):
            if not self.thread_lock.acquire(False):
                return
            image_cv = self.bridge.imgmsg_to_cv2(image_msg)
    
            self.detection(image_cv)
            
            if self.debugging:
                try:
                    self.pub_image.publish(\
                            self.bridge.cv2_to_imgmsg(image_cv, "bgr8"))
                except CvBridgeError as e:
                    print(e)
            self.thread_lock.release()
    
    
    def detection(self,  image_cv):
        for i in self.images:
            image_cv_ = image_cv.copy()
            result = cv2.matchTemplate(image_cv, i, cv2.TM_CCOEFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            top_left = max_loc
            w, h = i.shape[::-1]
            bottom_right = (top_left[0] + w, top_left[1] + h)
            
            cv2.rectangle(image_cv_,top_left, bottom_right, 255, 2)
            cv2.imshow("found", image_cv_)


