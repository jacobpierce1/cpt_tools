INC = ../include/
SRC = ../source/
OBJ = ../obj/

EXE_NAME = gui.exe


DEFINES = -DUSE_GUI # -DUSE_TDC -DUSE_CARIBU
WX_INCLUDE = `wx-config --cxxflags --libs`

all :  gui.exe

gui.exe :  $(SRC)/gui.cpp $(INC)/gui.h $(SRC)histo_image.cpp $(INC)histo_image.h
	g++ $(DEFINES) -I ../include ../source/histo_image.cpp ../source/gui.cpp $(WX_INCLUDE) -o $(EXE_NAME)



# $(OBJ)/mathplot.o : $(SRC)/mathplot.cpp $(INC)/mathplot.h
# 	g++ -I $(INC) -c $(SRC)/mathplot.cpp `wx-config --cxxflags --libs` -o $(OBJ)/mathplot.o


bitmap_test.exe : ../source/bitmap_test.cpp
	g++ -I $(INC) $(WX_INCLUDE) $(SRC)bitmap_test.cpp -o bitmap_test.exe

# wx_test :
# 	g++ ../source/wxWidgets_test.cpp `wx-config --cxxflags --libs` -o widget_test
.PHONY: clean
clean :
	rm $(EXE_NAME)
	rm ../obj/*

