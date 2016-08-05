#include "stdafx.h"

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

#define HandleResult(res,place) if (res!=XI_OK) {printf("Error after %s (%d)\n",place,res);goto finish;}

char fifoLocation[] = "CppToPythonFifo";

int _tmain(int argc, _TCHAR* argv[])
{
    
    // image buffer
    XI_IMG image;
    memset(&image,0,sizeof(image));
    image.size = sizeof(XI_IMG);

    // Sample for XIMEA API V4.05
    HANDLE xiH = NULL;
    XI_RETURN stat = XI_OK;
    
    // Retrieving a handle to the camera device 
    printf("Opening first camera...\n");
    stat = xiOpenDevice(0, &xiH);
    HandleResult(stat,"xiOpenDevice");
    
    // Setting "exposure" parameter (10ms=10000us)
    stat = xiSetParamInt(xiH, XI_PRM_EXPOSURE, 10000);
    HandleResult(stat,"xiSetParam (exposure set)");
    
    // Note:
    // The default parameters of each camera might be different in different API versions
    // In order to ensure that your application will have camera in expected state,
    // please set all parameters expected by your application to required value.
    
    printf("Starting acquisition...\n");
    stat = xiStartAcquisition(xiH);
    HandleResult(stat,"xiStartAcquisition");
    
    while(1) {
        // getting image from camera
        //We want to open the pipe before we start our stream.
        //NOTE: the pipe is halting, will not continue until receiving end is
        //      connected
        mkfifo(fifoLocation, 0666);
        //this is the blocking operation
        printf("Waiting for receiving end of pipe to connect to valmar...\n");
        int fifo = open(fifoLocation, O_WRONLY);
        stat = xiGetImage(xiH, 5000, &image);
        HandleResult(stat,"xiGetImage");
        printf("Attempting to write image to fifo\n");
        write(fifo, image.bp, image.bp_size);
        close(fifo);
    }
    
    printf("Stopping acquisition...\n");
    xiStopAcquisition(xiH);
    xiCloseDevice(xiH);
finish:
    printf("Done\n");
    return 0;
}

