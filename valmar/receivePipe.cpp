#include "stdafx.h"

#include <m3api/xiApi.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>

#define TEST_COUNT 10
#define TEST_BUFFER_LENGTH 1000000
#define FIFO_LOCATION "CppToPythonFifo"

int main(void) {
    printf("Attempting to connect to the write pipe...\n");
    register int fifo = open(FIFO_LOCATION, O_RDONLY);
    // image buffer
    XI_IMG image;
    memset(&image,0,sizeof(image));
    image.size = sizeof(XI_IMG);

    for(int index = 0; index < TEST_COUNT; index++) {
        printf("Waiting on %d frame\n", index);
        read(fifo, image.bp, image.size);
        printf("Received %d frame of %d bytes of length\n", index, image.size);
        //memset(image, 0, sizeof(XI_IMG));
    }
    close(fifo);
    return EXIT_SUCCESS;
}
