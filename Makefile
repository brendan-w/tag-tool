


# files and paths

HEADERS = utils.h
OBJ     = main.o \
          utils.o



# compile settings

CXX=g++
CXXFLAGS= -std=c++11 -Wall -Wextra -pedantic -ggdb
LIBS=



# targets

all:tag

tag: $(OBJ)
	$(CXX) -o $@ $^ $(CXXFLAGS) $(LIBS)

%.o: %.c $(HEADERS)
	$(CXX) -c -o $@ $< $(CXXFLAGS)

.PHONY: clean
clean:
	rm -f *.o tag

