
/**
   Data specifically that the daq generates and returns
*/
class DaqTelemetry
{
  public:
    double systemVoltage;//voltage coming off the batteries
    double systemCurrent;//system current
    double systemRpm;//computed rpm coming off the encoder
    double frontDistance; //computed distance from the object in front
    double backDistance; //computed distance from the object in back
};
