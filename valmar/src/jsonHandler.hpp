#include "includes.hpp"

/**
* JsonSettings is a class that deserializes the settings.json
* into an easily understood c++ class
*/
class JsonSettings {
    private:
        bool enabled;

        int framerate;
        int exposure_us;
        int gain;
        double gamma_y;
        double sharpness;
        
        int image_queue_size;

        double psnr_threshold;
        int num_frames_to_process;

        string write_location;
        double pixel_ratio;
        int ibeam_offset;

        void setCameraProperties();
    public:
        bool isEnabled();
        
        int getIBeamOffset();
        void setIBeamOffset(int offset);

        int getFrameRate();
        int getExposureTime();
        int getGain();
        double getGammaLuminosity();
        double getSharpness();

        double getPsnrThreshold();

        void refreshAllData(string filename);
};

