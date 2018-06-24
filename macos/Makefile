

# all:
# 	g++  hptdc_driver_3.4.3_x86_c_wrap.lib #  test.cpp -o run 

SRC = ../source/
INC = ../include/
OBJ = ../obj/

all : gui.o 
	;


gui.o : $(SRC)/gui.cpp $(INC)/gui.h
	g++ -c $^ -o $(OBJ)/gui.o


clean :
	rm $(OBJ)/*


.PHONY:
	all
	clean
