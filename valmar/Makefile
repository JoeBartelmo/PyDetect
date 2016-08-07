CXX=g++
MAIN_SOURCES=capturePipe.cpp
MAIN_SOURCES+=xiApiPlusOcv.cpp
MAIN_OBJECTS=$(MAIN_SOURCES:.cpp=.o)
TEST_SOURCES=receivePipe.cpp
TEST_OBJECTS=$(TEST_SOURCES:.cpp=.o)
PROGRAM=capturePipe
TEST_PROGRAM=receivePipe

all: $(PROGRAM) $(TEST_PROGRAM)

$(PROGRAM): $(MAIN_SOURCES)
	$(CXX) $(MAIN_SOURCES) -o $(PROGRAM) -lm3api -std=c++11 -lopencv_core -lopencv_highgui -lopencv_imgproc -L/usr/local/lib

$(TEST_PROGRAM): $(TEST_SOURCES)
	$(CXX) $(TEST_SOURCES) -o $(TEST_PROGRAM) -lm3api -std=c++11

.cpp.o: $(patsubst %.cpp,%.o,$(wildcard *.cpp))
	$(CXX) -g -c $< -o $@


xiApiPlusOcv.o: xiApiPlusOcv.cpp
	g++ -c xiApiPlusOcv.cpp -I . -I /usr/local/include/ -g3 -Wall -c -fmessage-length=0

clean:
	rm -f $(PROGRAM) $(MAIN_OBJECTS)
	rm -f $(TEST_PROGRAM) $(TEST_OBJECTS)

install:
	cp $(PROGRAM) ../../bin
