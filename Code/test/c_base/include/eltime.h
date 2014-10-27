#ifndef ELTIME_H
#define ELTIME_H

/*
  Functions for finding elapsed time in between
  trigger runs
*/

#include <time.h>

int timeval_subtract(struct timeval *result, 
		     struct timeval *t2, 
		     struct timeval *t1);

void timeval_print(struct timeval *tv);

#endif
