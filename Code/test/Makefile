nilibs=-lnidaqmxbase -ldaqtriggerbase
includes=-I../c_base/include
flags= -Wall
cc=gcc
lib_path=-Llib/usr/local/lib

src_files = c_test
      
all : $(src_files)

% : %.c
	$(cc) $(lib_path) $(includes) $< $(nilibs) -o $@

clean :
	rm -f $(src_files)
