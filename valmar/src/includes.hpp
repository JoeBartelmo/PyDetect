/**
* We shove all includes in here to make our lives easier across all these
* different files
*/

#if !defined(VALMAR_INCLUDES) 
#define VALMAR_INCLUDES
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
#include <opencv2/opencv.hpp>

using namespace cv;
using namespace std;
using json = nlohmann::json;
#endif

