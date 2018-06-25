INC = ../include/
SRC = ../source/
OBJ = ../obj/

DEFINES = -DUSE_GUI # -DUSE_TDC -DUSE_CARIBU
WX_INCLUDE = `wx-config --cxxflags --libs`

all : $(OBJ)/mathplot.o gui.exe

gui.exe : $(OBJ)/mathplot.o $(SRC)/gui.cpp $(INC)/gui.h
	g++ $(DEFINES) $(OBJ)/mathplot.o -I ../include ../source/gui.cpp $(WX_INCLUDE) -o gui.exe



$(OBJ)/mathplot.o : $(SRC)/mathplot.cpp $(INC)/mathplot.h
	g++ -I $(INC) -c $(SRC)/mathplot.cpp `wx-config --cxxflags --libs` -o $(OBJ)/mathplot.o 


# wx_test :
# 	g++ ../source/wxWidgets_test.cpp `wx-config --cxxflags --libs` -o widget_test
clean :
	rm ../obj/*


.PHONY : all clean 
