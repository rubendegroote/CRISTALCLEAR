
#include <stdio.h>
#include "daq_trigger_base.h"


int main(void) {
  /* Testing */
  printf("Setting parameters\n");
  setParameters("/Dev1/ai8", 1000, "/Dev1/PFI0", 10);


  printf("Beginning acquire\n");
  acquire();

}

