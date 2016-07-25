// Sample for XIMEA Software Package V2.57

#include "stdafx.h" 
#include "..\include\xiApi.h" 
#include <memory.h>
#define errorCheck(res,place) if (res!=XI_OK) {printf("Error after %s (%d)",place,res); closeAndEnd();}

/* sets up a pointer with which to store the image we are working with*/
XI_IMG image;
// image.size = sizeof(XI_IMG);
// image.bp = NULL;
// image.bp_size = 0;

/*device values*/
HANDLE xiH = NULL; //xiH --> ximea camera handle
XI_RETURN status = XI_OK;

/*camera modifiers*/
int shutter_type = 0; //indicates a global shutter
float framerate = 100.0; //in Hz
int exposure_us = 100; //in microseconds

/*image modifiers*/
float gain = 0; //in decibels
float gamma_y = 0.47; //range (0,1)
float sharpness = 0; //range (-4,4)

/*system modifiers*/
int image_queue_size= 150; // 150 images in queue
//it may be necessary to also set the phyical buffer size.
//1.2MB ~= 3images

/*processing modifers*/
double psnr_threshold;
int num_frames_to_process;




void cameraSetup()
{
    /*opening device*/
    status = xiOpenDevice(0, &xiH);
    errorCheck(status,"xiOpenDevice");
    
    /* setting system modifers */
    status = xiSetParamInt(handle, XI_PRM_BUFFERS_QUEUE_SIZE, image_queue_size);
    errorCheck(status,"XI_PRM_BUFFERS_QUEUE_SIZE");
    
    /* setting capture modifiers */
    status = xiSetParamInt(xiH, XI_PRM_SHUTTER_TYPE, shutter_type);
    errorCheck(status,"XI_PRM_SHUTTER_TYPE");
    status = xiSetParamInt(xiH, XI_PRM_EXPOSURE, exposure_us);
    errorCheck(status,"XI_PRM_EXPOSURE");
    status = xiSetParamInt(xiH, XI_PRM_FRAMERATE, framerate)
    errorCheck(status,"XI_PRM_FRAMERATE");
    
    /* setting image modifiers */
    status = xiSetParamFloat(xiH, XI_PRM_GAIN, gain);
    errorCheck(status,"XI_PRM_GAIN");
    status = xiSetParamFloat(xiH, XI_PRM_SHARPNESS, sharpness);
    errorCheck(status,"XI_PRM_SHARPNESS");
    status = xiSetParamFloat(xiH, XI_PRM_GAMMAY, gamma_y);
    errorCheck(status, "XI_PRM_GAMMAY");

}

void closeAndEnd()
{
    xiStopAcquistion();
    xiCloseDevice(xiH);
}

void main()
{
    cameraSetup()
    closeAndEnd()

}



// double performPSNR()
// {
//     status = xiGetImage(xiH, &image);
//     errorCheck(status,"xiGetImage");
//     //Everything here can be gpu accelerated in OPENCV
//     //We should setup openCV for Tegra - I believe this will automatically GPU accelerate everything on the TK1
// }



// double generateGapWidth()
// {
//     for(int i = 0, i < num_frames_to_process, i = i + 1)
//     {
//         //Do processing here to generate an array of gap width values


//     }



// }






// int main ()
// {
//     double psnr;
//     cameraSetup();
//     // while(TRUE)
//     // {
//     //     xiStartAcquisition(xiH);
//     //     psnr = performPSNR();
//     //     if(psnr > psnr_threshold)
//     //     {
//     //         generateGapWidth();
//     //     }
//     // }
// }




/* uncomment the following and comment the other cameraSetup() if you don't desire error checking */

// void cameraSetup();
// {
//     /* sets up a pointer with which to store the image we are working with*/
//     /*opening device*/
//     xiOpenDevice(0, &xiH);

//     /* system modifers */
//     xiSetParamInt(handle, XI_PRM_BUFFERS_QUEUE_SIZE, image_queue_size);
        
//     /* capture modifiers */
//     xiSetParamInt(xiH, XI_PRM_SHUTTER_TYPE, shutter_type);
//     xiSetParamInt(xiH, XI_PRM_EXPOSURE, exposure_us);
//     xiSetParamInt(xiH, XI_PRM_FRAMERATE, framerate)

//     /* image modifiers */
//     xiSetParamFloat(xiH, XI_PRM_GAIN, gain);
//     xiSetParamFloat(xiH, XI_PRM_SHARPNESS, sharpness);
//     xiSetParamFloat(xiH, XI_PRM_GAMMAY, gamma_y);
// }
