CXX=g++
MAIN_SOURCES=src/xiApiPlusOcv.cpp
MAIN_SOURCES+=src/jsonHandler.cpp
MAIN_SOURCES+=src/calibration.cpp
MAIN_SOURCES+=src/measurements.cpp
MAIN_SOURCES+=src/main.cpp
MAIN_OBJECTS=$(MAIN_SOURCES:.cpp=.o)
PROGRAM=valmar

all: $(PROGRAM)

$(PROGRAM): $(MAIN_SOURCES)
	$(CXX) $(MAIN_SOURCES) -o $(PROGRAM) -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib
	$(CXX) $(MAIN_SOURCES) -o $(PROGRAM)-debug -lm3api -std=c++11 -lopencv_core -lopencv_calib3d -lopencv_features2d -lopencv_highgui -lopencv_imgproc -L/usr/local/lib -D DEBUG

.cpp.o: $(patsubst %.cpp,%.o,$(wildcard *.cpp))
	$(CXX) -g -c $< -o $@

clean:
	rm -f $(PROGRAM) $(MAIN_OBJECTS)

