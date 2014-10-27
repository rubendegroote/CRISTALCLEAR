nilibs=-lnidaqmxbase
includes=-I./include
flags1= -c -Wall -fPIC
ldflags= -shared
cc=gcc

output=libcdaq
dir=build

srcs= c_daq.c eltime.c
objects= $(srcs:.c=.o)

      
all : 
	$(cc)  $(includes) $(flags1) $(srcs) $(nilibs) 
	$(cc) $(ldflags) -o $(dir)/$(output).so $(objects)
	rm -f $(objects)
	cp $(dir)/$(output).so /usr/local/lib

clean :
	rm -f $(dir)/$(output).so $(objects)


