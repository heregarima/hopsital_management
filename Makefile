CXX = g++
CXXFLAGS = -std=c++11 -Wall -O2
LDFLAGS = -lws2_32 -lwsock32
TARGET = medaxis_server.exe

all: $(TARGET)

$(TARGET): medaxis_server.cpp
	$(CXX) $(CXXFLAGS) medaxis_server.cpp -o $(TARGET) $(LDFLAGS)

clean:
	del /Q $(TARGET) *.o

