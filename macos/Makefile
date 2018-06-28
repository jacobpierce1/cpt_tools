INC = ../include/
SRC = ../source/
OBJ = ../obj/

EXE_NAME = gui.exe

OBJS = $(OBJ)histo_image.o $(OBJ)tdc.o $(OBJ)global.o

DEFINES = -DUSE_GUI # -DUSE_TDC -DUSE_CARIBU
WX_INCLUDE = `wx-config --cxxflags --libs`

all :  gui.exe   # $(OBJ)tdc.o $(OBJ)histo_image.o


gui.exe :  $(SRC)/gui.cpp $(INC)/gui.h $(OBJS)
	g++ $(DEFINES) -I ../include $(OBJS) ../source/gui.cpp $(WX_INCLUDE) -o $(EXE_NAME)


$(OBJ)%.o : $(SRC)%.cpp $(INC)%.h
	g++ -c -I $(INC) $< $(WX_INCLUDE) -o $@


.PHONY: clean
clean :
	rm -f $(EXE_NAME)
	rm -f ../obj/*

