#include "includes.hpp"
/**
* CalibrationEntity is a class that does calculations to determine the
* calibrated constant for valmar and store calibrated entities
*/
class CalibrationEntity {
    private:
        Mat calibratedMatrix;
        double calibratedConstant;
    public:
        double getCalibratedConstant();
        Mat getCalibratedMatrix();
        double getPSNR(const Mat& I2);
        double runCalibration(xiAPIplusCameraOcv *cam, bool debug); 
        double runCalibration(xiAPIplusCameraOcv *cam); 
};

