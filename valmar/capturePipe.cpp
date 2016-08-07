#include "stdafx.h"
#include "xiApiPlusOcv.hpp"
#include "json.hpp"

#include <m3api/xiApi.h>
#include <memory.h>
#include <sys/wait.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fstream>

#define FIFO_LOCATION "CppToPythonFifo"

using json = nlohmann::json;
using namespace cv;

//http://docs.opencv.org/2.4/doc/tutorials/highgui/video-input-psnr-ssim/video-input-psnr-ssim.html#image-similarity-psnr-and-ssim
double getPSNR(const Mat& I1, const Mat& I2)
{
    Mat s1;
    absdiff(I1, I2, s1);       // |I1 - I2|
    s1.convertTo(s1, CV_32F);  // cannot make a square on 8 bits
    s1 = s1.mul(s1);           // |I1 - I2|^2

    Scalar s = sum(s1);         // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    if( sse <= 1e-10) // for small values return zero
        return 0;
    else
    {
        double  mse =sse / (double)(I1.channels() * I1.total());
        double psnr = 10.0 * log10((255 * 255) / mse);
        return psnr;
    }
}

int sendImagesToPipe(xiAPIplusCameraOcv *cam, int images_to_load) {
    printf("PSNR Threshold met, sending next %d frames\n", images_to_load);
    int fifo, img_size, frameIndex;
    Mat cv_mat_image;
    
    printf("Waiting for receiving end of pipe to connect to valmar...\n");
    for(frameIndex = 0; frameIndex < images_to_load; frameIndex++) {
        //this is the blocking operation
        cv_mat_image = (*cam).GetNextImageOcvMat();
        fifo = open(FIFO_LOCATION, O_WRONLY);
        img_size = cv_mat_image.total() * cv_mat_image.elemSize();
        printf("Image size of cv::MAT is %d bytes\n", img_size);
        write(fifo, cv_mat_image.data, img_size);
        close(fifo);
    }
    return 1;
}

json readFileAsJson(string fileName) {
    printf("Attempting to load in file %s\n", fileName.c_str());
    std::ifstream t(fileName);
    std::stringstream buffer;
    buffer << t.rdbuf();
    json returnedJSON = json::parse(buffer.str());
    return returnedJSON;
}

int _tmain(int argc, _TCHAR* argv[])
{ 
    //load settings
    string settingsFile = "command.json";
    switch(argc) {
        case 1:
            break;
        case 2:
            settingsFile = argv[1];
            break;
        default:
            printf("Usage: capturePipe [optional settings file.json]%d", argc);
            return EXIT_FAILURE;
    }

    json settings = readFileAsJson(settingsFile);

    if(settings["command"]["enabled"] == false) {
        return EXIT_SUCCESS;
    }
    
    // Sample for XIMEA OpenCV
    xiAPIplusCameraOcv cam;

    // Retrieving a handle to the camera device
    printf("Opening first camera...\n");
    cam.OpenFirst();
    
    //Set exposure
    cam.SetExposureTime(settings["capture"]["exposure_us"]); //10000 us = 10 ms
    cam.SetGain(settings["capture"]["gain"]);
    //cam.SetFrameRate(settings["capture"]["framerate"]);
    cam.SetGammaLuminosity(settings["capture"]["gamma_y"]);
    cam.SetSharpness(settings["capture"]["sharpness"]);
    // Note: The default parameters of each camera might be different in different API versions
    
    printf("Starting acquisition...\n");
    cam.StartAcquisition();
        
    //We want to open the pipe before we start our stream.
    //NOTE: the pipe is halting, will not continue until receiving end is
    //      connected
    mkfifo(FIFO_LOCATION, 0666);
   
    printf("Waiting for PSNR Trigger...\n");
    while(1) {
        // getting image from camera
        try {
            const Mat mat1 = cam.GetNextImageOcvMat();
            const Mat mat2 = cam.GetNextImageOcvMat();
            
            double psnr;
            if ((psnr = getPSNR(mat1, mat2)) >= (double)settings["processing"]["psnr_threshold"]) {
                printf("PSNR of %f reached threshold of %d\n", psnr, (int)settings["processing"]["psnr_threshold"]);
                sendImagesToPipe(&cam, settings["processing"]["num_frames_to_process"]);
            }
        }
	catch(xiAPIplus_Exception& exp){
            printf("Error:\n");
            exp.PrintError();
            cvWaitKey(200);
	}
    }
    
    cam.StopAcquisition();
    cam.Close();
    printf("Done\n");
}

