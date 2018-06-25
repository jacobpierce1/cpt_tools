INC = ../include/
SRC = ../source/
OBJ = ../obj/


all : $(OBJ)/mathplot.o gui.exe

gui.exe : $(OBJ)/mathplot.o
	g++ $(OBJ)/mathplot.o -I ../include ../source/gui.cpp `wx-config --cxxflags --libs` -o gui.exe



$(OBJ)/mathplot.o : $(SRC)/mathplot.cpp $(INC)/mathplot.h
	g++ -I $(INC) -c $(SRC)/mathplot.cpp `wx-config --cxxflags --libs` -o $(OBJ)/mathplot.o 


# wx_test :
# 	g++ ../source/wxWidgets_test.cpp `wx-config --cxxflags --libs` -o widget_test
clean :
	rm ../obj/*


.PHONY : all clean 
