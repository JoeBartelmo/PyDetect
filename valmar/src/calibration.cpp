#include "includes.hpp"

#if !defined VALMAR_CALIBRATION
#define VALMAR_CALIBRATION
#include "calibration.hpp"
#define PATTERN_COLS 2
#define PATTERN_ROWS 2
#define CALIBRATION_ATTEMPTS 10
#endif


void _displayAndSave(Mat image, String image_name){
    cout << "displaying and saving "+image_name << std::endl;
    cv::imshow(image_name,image);
    cv::imwrite(image_name,image);
}
//http://docs.opencv.org/2.4/doc/tutorials/highgui/video-input-psnr-ssim/video-input-psnr-ssim.html#image-similarity-psnr-and-ssim
double CalibrationEntity::getPSNR(const Mat& I2)
{
    Mat s1;
    absdiff(calibratedMatrix, I2, s1);       // |I1 - I2|
    s1.convertTo(s1, CV_32F);  // cannot make a square on 8 bits
    s1 = s1.mul(s1);           // |I1 - I2|^2

    Scalar s = sum(s1);         // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    if( sse <= 1e-10) { // for small values return zero
        return 0;
    }
    else {
        double mse = sse / (double)(calibratedMatrix.channels() * calibratedMatrix.total());
        double psnr = 10.0 * log10((255 * 255) / mse);
        return psnr;
    }
}

cv::Mat CalibrationEntity::getCalibratedMatrix() {
    return calibratedMatrix;
}

double CalibrationEntity::getCalibratedConstant() {
    return calibratedConstant;
}

double CalibrationEntity::runCalibration(xiAPIplusCameraOcv *cam, bool debug) {
    Mat startMatrix = cam->GetNextImageOcvMat();
    Mat matrixWithCorners;
    
    _displayAndSave(startMatrix, "startImg.png");
    if (debug) {
        calibratedMatrix = startMatrix;
        return 0;
    }

    printf("[VALMAR] Attemting to find chessboard\n");
    for(int attempts = 0; attempts < CALIBRATION_ATTEMPTS; attempts++) {
        if (findChessboardCorners(startMatrix, 
                                Size(PATTERN_COLS, PATTERN_ROWS), 
                                matrixWithCorners, 
                                CALIB_CB_FAST_CHECK)) {
            break;
        }
        if (attempts == CALIBRATION_ATTEMPTS - 1) {
            printf("[VALMAR] Could not find chessboard after %d attempts\n", CALIBRATION_ATTEMPTS);
            return -1;
        }
        startMatrix = cam->GetNextImageOcvMat();
        _displayAndSave(startMatrix, std::to_string(attempts) + ".png");
    }    
}

double CalibrationEntity::runCalibration(xiAPIplusCameraOcv *cam) {
    return runCalibration(cam, false);
}
 
