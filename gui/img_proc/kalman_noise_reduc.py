# -*- coding: utf-8 -*-
"""
Created on Mon Jun 06 14:46:34 2016

Use a Kalman Filter to remove Gaussian noise from an image

This is a first attempt at trying to remove Gaussian noise from an image
without removing valuable information from the image. The noise removal 
method will require a stream of images upon which a discreet Kalman Filter
iteration will operate per pixel (or pixel grouping). As the state k (frames)
increases, noise will be factored out through linear quadratic estimation, 
and the iteration will converge at an estimation of the true signal.

DEPENDENCIES
============

Module: cv2, numpy

DEVELOPMENT METADATA
====================

@copyright:: Copyright (C) 2016 RIT Hyperloop Imaging Team

@license:: LGNU

@author:: Ryan Hartzell

@email:: RIT.CIS.Hyperloop@gmail.com

@disclaimer:: Neither the members of the RIT Hyperloop Imaging Team nor the 
              Rochester Institute of Technology make any representation 
              about the suitability of this software for any purpose, 
              specifically the ability to prevent catastrophic failures in the
              proposed Hyperloop system. It is provided "as is" without any 
              express or implied warranty whatsoever. The RIT Hyperloop Imaging
              Team will not be liable for any indirect, direct, or 
              consequential damages which may result from the use of this
              software.
              
HISTORY
=======

1.0.dev1
    * [06 June 2016 : Ryan Hartzell] 
        * Noise reduction method, documentation, and initial test harness prep

1.0.dev2
    * [14 June 2016 : Nate Dileas & Ryan Hartzell]
        * Method editted for speed and accuracy, usability/project integration

"""

import numpy as np
import cv2

def kalman_noise_reduc_new(stream, R=20):
    """ A method for reducing Gaussian noise in an image by Kalman Filtering. """
    
    #   NOTE: R=280 for reasonable progression. R>=500 to show actual signal
    #   at k=3 or k=4. Instead of oscillating around true signal, the filter
    #   bypasses it and continues trend toward white IFF x_hat_adj is not
    #   made into uint8, rounded integers. I think that with many states k,
    #   the new model below will work for us much better, as the beam
    #   "emerges" with less noise (R=20). However, I'm still testing, and the
    #   first approach yields a quicker, more accurate-to-truth image k~3
    
    
    k = 0 #   set initial state of Kalman Filter given first frame
    
    x_hat_adj = [] #   set up adjusted x_hat and p_k storage
    p_k_adj = []
    
    cap = cv2.VideoCapture(stream)
    while(cap.isOpened()): #   need a different gauge to keep while loop open
    
        ret, frame = cap.read() #   gives us a TRUE or FALSE and an image
        
        if ret == False: #   makes sure there is still a stream to pull from
            break
        
        elif k == 0:            #   check state, assign variables as such
            x_hat_est = 0.0
            p_k_est = 1.0
        
        elif k > 0:
            x_hat_est = x_hat_adj            
            
            p_k_est = p_k_adj
            
        else:
            pass
        
        K_gain = p_k_est/float(p_k_est + R)   #   calculate Kalman Gain
        
        z_k = frame #   Begin kalman math stuff for given state
        
        x_hat_adj = np.uint8(np.rint(x_hat_est + K_gain * (z_k - x_hat_est)))
        
        p_k_adj = (1.0 - K_gain) * p_k_est
        
        cv2.imshow('Kalman Filtered Output',x_hat_adj) #   display results
        key = cv2.waitKey(0) & 0xFF #as specified by the waitKey documentation
        print 'Hit \'Esc\' to destroy the window, or \'s\' to save the image.'

        if key == 27:         # wait for ESC key to exit
            cv2.destroyAllWindows()
        elif key == ord('s'): # wait for 's' key to save and exit
            cv2.imwrite('KalmanIteration_' + str(k) + '.png',x_hat_adj)
            cv2.destroyAllWindows()
        
        
        k += 1 #   increase state by one, recursive program continues

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    vid = 'KalmanTestVid.avi'        
    kalman_noise_reduc_new(vid) #   Read in a video (or stream)
