# PyDetect
This project is a collaboration of the hyperloop software development team at RIT. Overall, this project is centered around our rover (Codename: Mars). As a whole, this is a collection of submodules that are coupled together to preform higher level tasks.

### Goal
Originally, we were told that "A camera on top of an RC car" would be optimal" We have decided to go above and beyond expectations. Mars is a rover system that is capable of many operations. 
1. Communication between the rover and the client of vital telemetry data
 * Rover operations (battery, current, other useful information) 
 * IBeam data (current ibeam and gap data in between ibeams)
 * Command codes that allow instruction from client to the rover
2. Visual communication between the rover and the client.
3. An inspection system capable of detecting foreign object debris in the hyperloop tube
4. Some method for storage of the data

### Program Structure
We have seperated this project into several submodules as mentioned heretofore. The primary reason is an attempt to make this project loosely coupled and allow for testing of independant modules. The module sub structure thusly is given in the following table:

|Module  | Module Dependencies | Description |
|--------|---------------------|--------------|
| Maven | None | Responsible for capturing and relaying RTSP streams. Interface command line
| Valmar | None | Responsible for obtaining beam gap data and other IBeam related data
| Mars  | Valmar, Maven | Responsible for control of mars and control of the rover
| Server | Mars | Responsible for Client Communication and relay to the mars controller
| Client | Server, GUI | Responsible for communication between the server and self. Responsible for piping data to the GUI  
| GUI | Client | Responsible for diplay of data in a user friendly way from the client 
| setup-tk1| None | Will automatically install all dependencies for the tk1 (rover) 

### Rover Dependencies
  - OpenCV4Tegra - http://elinux.org/Jetson/Installing_OpenCV
  - Python - https://www.python.org/downloads/
  - NodeJS - https://nodejs.org/en/download/
  - VLC    - http://www.videolan.org/vlc/index.html

### Client Dependencies
  - OpenCV - http://opencv.org/downloads.html
  - Python - https://www.python.org/downloads/
  - Tkinter - http://www.tkdocs.com/tutorial/install.html

### Workflow
| Name   | Position | Responsibilities |
|----------|-------------|---------|
| Joe Bartelmo|  Dev Lead | Software development and maintaining code
| Jeff Maggio | Tech Lead | Outlining features for implementation for the software developers
| Nathan Dileas | Developer | Software Development

### Version
1.0.2

